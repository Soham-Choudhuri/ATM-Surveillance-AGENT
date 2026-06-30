# 🌍 Remote Access Guide: Setting up Tailscale

This guide explains how to securely access the AwareX Multimodal Autonomous Surveillance System from anywhere in the world (like a college campus or a coffee shop) while the heavy AI processing runs safely on your powerful home PC.

We will use **Tailscale**, a free and highly secure zero-configuration VPN. It creates a private, encrypted mesh network between your devices, making them behave as if they are connected to the exact same home Wi-Fi router.

---

## 1. Why Tailscale?
- **High Security**: Your video feeds and administrative controls are never exposed to the public internet. Only devices logged into your Tailscale account can access the dashboard.
- **High Performance**: Tailscale establishes direct peer-to-peer connections. Because it bypasses traditional relay servers, video streaming latency is incredibly low.
- **Zero Firewall Configuration**: It automatically traverses NATs and bypasses Windows Firewall restrictions without requiring dangerous port-forwarding on your home router.

---

## 2. Step 1: Setting up the Host Machine (Your Home PC)
Your Home PC is the "Server" that actually runs the AI models and the cameras.

1. Go to [tailscale.com](https://tailscale.com/) and create a free account.
2. Download and install the Tailscale Windows client on your Home PC.
3. Open Tailscale from the Windows System Tray (bottom right corner) and click **Log In**.
4. Once authenticated, click on the Tailscale icon in the system tray again. You will see an IP address at the very top of the menu (e.g., `100.85.22.14`). 
5. **Copy this IP address.** This is your Home PC's secure, permanent Tailscale IP.

---

## 3. Step 2: Setting up the Client Device (College Laptop / iPad / Phone)
This is the device you will use to remotely view the dispatch dashboard.

1. Download the Tailscale app on your remote device (available for Windows, macOS, iOS, Android, and Linux).
2. Open the app and **Log In using the exact same account** you used in Step 1.
3. Ensure the VPN toggle is switched to **Active / Connected**.

> [!NOTE]
> Tailscale must be actively running on both devices for the connection to work!

---

## 4. Step 3: Accessing the Dashboard Remotely
Because we have configured the Next.js server to act as a secure proxy, you only need to connect to Port `3000`.

1. Ensure the AwareX system is actively running on your Home PC (via `run.bat`).
2. On your remote College Laptop, open any web browser.
3. In the URL bar, type the Tailscale IP of your Home PC (from Step 1) followed by `:3000`. 
   
   **Example:**
   ```text
   http://100.85.22.14:3000
   ```
   *To access the Central Dispatch view specifically, use `http://100.85.22.14:3000/dispatch`*

4. You're done! The dashboard will load instantly, and the real-time video feed and AI incident logs will stream flawlessly across the country.

---

## 5. Troubleshooting & Tips

> [!TIP]
> **Dynamic APIs**: Because of our dynamic `window.location.hostname` architecture, the frontend will automatically detect that you are using a `100.x.x.x` Tailscale IP and will route all internal API calls through it flawlessly. No code changes are required!

- **Dashboard isn't loading**: Ensure `run.bat` on the host machine launched Next.js with the `-H 0.0.0.0` flag (which allows external connections).
- **Video feed is laggy**: Tailscale usually creates direct P2P connections. If you are on an extremely restrictive college network (Strict NAT), Tailscale might fallback to a "DERP Relay". This adds latency. Try switching your laptop to a mobile hotspot to see if performance improves.
- **Can't access Admin Portal**: The Admin portal (`/admin`) and Logs database (`/logs`) are fully accessible via Tailscale! However, you still need the `.admin_access` token file present in the root of the project on the Host PC for the backend to grant access.
