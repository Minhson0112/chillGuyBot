(function () {
    const authState = {
        ready: false,
        accessToken: null,
        user: null,
        guildId: null,
        channelId: null,
        error: null,
    };

    window.chillGuyDiscordAuth = authState;

    function normalizeError(error) {
        if (!error) {
            return null;
        }

        return {
            name: error.name || null,
            message: error.message || String(error),
            stack: error.stack || null,
        };
    }

    function logAuthStep(message, data = {}) {
        console.info(message, data);

        fetch("/api/client-log", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                message,
                data,
            }),
        }).catch((error) => {
            console.warn("Discord Activity client log failed:", error);
        });
    }

    async function initDiscordAuth() {
        logAuthStep("Discord Activity auth init started.");

        const clientId = import.meta.env?.VITE_DISCORD_CLIENT_ID || "";
        if (!clientId) {
            logAuthStep("Discord Activity auth skipped: DISCORD_CLIENT_ID is not configured.");
            return authState;
        }

        logAuthStep("Discord Activity client id is configured.");

        try {
            logAuthStep("Discord Activity SDK import started.");
            const { DiscordSDK } = await import("@discord/embedded-app-sdk");

            logAuthStep("Discord Activity SDK import completed.");
            const discordSdk = new DiscordSDK(clientId);

            logAuthStep("Discord Activity SDK ready wait started.");
            await discordSdk.ready();
            logAuthStep("Discord Activity SDK ready completed.", {
                guildId: discordSdk.guildId || null,
                channelId: discordSdk.channelId || null,
            });

            logAuthStep("Discord Activity authorize started.");
            const { code } = await discordSdk.commands.authorize({
                client_id: clientId,
                response_type: "code",
                state: "",
                prompt: "none",
                scope: ["identify", "guilds"],
            });
            logAuthStep("Discord Activity authorize completed.", {
                hasCode: Boolean(code),
            });

            logAuthStep("Discord Activity token exchange request started.");
            const tokenResponse = await fetch("/api/discord/token", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ code }),
            });
            logAuthStep("Discord Activity token exchange response received.", {
                ok: tokenResponse.ok,
                status: tokenResponse.status,
            });

            if (!tokenResponse.ok) {
                throw new Error("Discord token exchange failed");
            }

            const { access_token: accessToken } = await tokenResponse.json();
            logAuthStep("Discord Activity token exchange completed.", {
                hasAccessToken: Boolean(accessToken),
            });

            logAuthStep("Discord Activity authenticate started.");
            const auth = await discordSdk.commands.authenticate({
                access_token: accessToken,
            });

            if (!auth) {
                throw new Error("Discord authenticate command failed");
            }

            logAuthStep("Discord Activity authenticate completed.", {
                userId: auth.user?.id || null,
            });

            authState.ready = true;
            authState.accessToken = accessToken;
            authState.user = auth.user || null;
            authState.guildId = discordSdk.guildId || null;
            authState.channelId = discordSdk.channelId || null;
            authState.sdk = discordSdk;

            logAuthStep("Discord Activity auth init completed.", {
                userId: authState.user?.id || null,
                guildId: authState.guildId,
                channelId: authState.channelId,
            });

            return authState;
        } catch (error) {
            authState.error = error;
            console.warn("Discord Activity auth is not ready:", error);
            logAuthStep("Discord Activity auth is not ready.", {
                error: normalizeError(error),
            });
            return authState;
        }
    }

    window.initChillGuyDiscordAuth = initDiscordAuth;
    initDiscordAuth();
})();
