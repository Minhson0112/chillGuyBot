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

    let logSequence = 0;

    function getDiscordQueryContext() {
        const queryParams = new URLSearchParams(window.location.search);

        return {
            frameId: queryParams.get("frame_id"),
            guildId: queryParams.get("guild_id"),
            channelId: queryParams.get("channel_id"),
            platform: queryParams.get("platform"),
            href: window.location.href,
        };
    }

    function getRedirectUri() {
        return `${window.location.origin}/`;
    }

    function withTimeout(promise, timeoutMs, timeoutMessage) {
        return Promise.race([
            promise,
            new Promise((_, reject) => {
                setTimeout(() => {
                    reject(new Error(timeoutMessage));
                }, timeoutMs);
            }),
        ]);
    }

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

    async function logAuthStep(message, data = {}) {
        const payload = {
            seq: ++logSequence,
            ...getDiscordQueryContext(),
            ...data,
        };

        console.info(message, payload);

        try {
            await fetch("/api/client-log", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    message,
                    data: payload,
                }),
            });
        } catch (error) {
            console.warn("Discord Activity client log failed:", error);
        }
    }

    async function initDiscordAuth() {
        await logAuthStep("Discord Activity auth init started.");

        const clientId = import.meta.env?.VITE_DISCORD_CLIENT_ID || "";
        if (!clientId) {
            await logAuthStep("Discord Activity auth skipped: DISCORD_CLIENT_ID is not configured.");
            return authState;
        }

        await logAuthStep("Discord Activity client id is configured.");

        try {
            const redirectUri = getRedirectUri();

            await logAuthStep("Discord Activity redirect uri resolved.", {
                redirectUri,
            });

            await logAuthStep("Discord Activity SDK import started.");
            const { DiscordSDK } = await import("@discord/embedded-app-sdk");

            await logAuthStep("Discord Activity SDK import completed.");
            const discordSdk = new DiscordSDK(clientId);

            await logAuthStep("Discord Activity SDK ready wait started.");
            await discordSdk.ready();
            await logAuthStep("Discord Activity SDK ready completed.", {
                guildId: discordSdk.guildId || null,
                channelId: discordSdk.channelId || null,
            });

            await logAuthStep("Discord Activity authorize started.", {
                prompt: "default",
                redirectUri,
            });
            const { code } = await withTimeout(
                discordSdk.commands.authorize({
                    client_id: clientId,
                    redirect_uri: redirectUri,
                    response_type: "code",
                    state: "",
                    scope: ["identify", "guilds"],
                }),
                30000,
                "Discord authorize timed out after 30 seconds",
            );
            await logAuthStep("Discord Activity authorize completed.", {
                hasCode: Boolean(code),
            });

            await logAuthStep("Discord Activity token exchange request started.");
            const tokenResponse = await fetch("/api/discord/token", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    code,
                    redirect_uri: redirectUri,
                }),
            });
            await logAuthStep("Discord Activity token exchange response received.", {
                ok: tokenResponse.ok,
                status: tokenResponse.status,
            });

            if (!tokenResponse.ok) {
                throw new Error("Discord token exchange failed");
            }

            const { access_token: accessToken } = await tokenResponse.json();
            await logAuthStep("Discord Activity token exchange completed.", {
                hasAccessToken: Boolean(accessToken),
            });

            await logAuthStep("Discord Activity authenticate started.");
            const auth = await discordSdk.commands.authenticate({
                access_token: accessToken,
            });

            if (!auth) {
                throw new Error("Discord authenticate command failed");
            }

            await logAuthStep("Discord Activity authenticate completed.", {
                userId: auth.user?.id || null,
            });

            authState.ready = true;
            authState.accessToken = accessToken;
            authState.user = auth.user || null;
            authState.guildId = discordSdk.guildId || null;
            authState.channelId = discordSdk.channelId || null;
            authState.sdk = discordSdk;

            await logAuthStep("Discord Activity auth init completed.", {
                userId: authState.user?.id || null,
                guildId: authState.guildId,
                channelId: authState.channelId,
            });

            return authState;
        } catch (error) {
            authState.error = error;
            console.warn("Discord Activity auth is not ready:", error);
            await logAuthStep("Discord Activity auth is not ready.", {
                error: normalizeError(error),
            });
            return authState;
        }
    }

    window.initChillGuyDiscordAuth = initDiscordAuth;
    initDiscordAuth();
})();
