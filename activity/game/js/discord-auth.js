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

    async function authorizeDiscordActivity(discordSdk, clientId) {
        const { code } = await discordSdk.commands.authorize({
            client_id: clientId,
            response_type: "code",
            state: "",
            prompt: "none",
            scope: ["identify", "guilds"],
        });

        const tokenResponse = await fetch("/api/discord/token", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ code }),
        });

        if (!tokenResponse.ok) {
            throw new Error("Discord token exchange failed");
        }

        const { access_token: accessToken } = await tokenResponse.json();

        const auth = await discordSdk.commands.authenticate({
            access_token: accessToken,
        });

        if (!auth) {
            throw new Error("Discord authenticate command failed");
        }

        authState.ready = true;
        authState.accessToken = accessToken;
        authState.user = auth.user || null;
        authState.guildId = discordSdk.guildId || null;
        authState.channelId = discordSdk.channelId || null;
        authState.sdk = discordSdk;
        authState.error = null;

        return authState;
    }

    async function initDiscordAuth() {
        const clientId = import.meta.env?.VITE_DISCORD_CLIENT_ID || "";
        if (!clientId) {
            console.info("Discord Activity auth skipped: DISCORD_CLIENT_ID is not configured.");
            return authState;
        }

        try {
            const { DiscordSDK } = await import("@discord/embedded-app-sdk");
            const discordSdk = new DiscordSDK(clientId);

            await discordSdk.ready();
            authState.sdk = discordSdk;

            return await authorizeDiscordActivity(discordSdk, clientId);
        } catch (error) {
            authState.error = error;
            console.warn("Discord Activity auth is not ready:", error);
            return authState;
        }
    }

    window.initChillGuyDiscordAuth = initDiscordAuth;
    initDiscordAuth();
})();
