
/**
 * @typedef {{
 *	channel: number
 *	hidden: boolean
 *	ssid: string
 *	bssid: string
 *	mac: string
 *	rssi: number
 *	status: "UNKNOWN" | "IDLE" | "CONNECTING" | "WRONG_PASSWORD" | "GOT_IP" | "NO_AP_FOUND"
 *	security: "OPEN" | "WEP" | "WPA-PSK" | "WPA2-PSK" | "WPA/WPA2-PSK"
 * }} WifiInstance
 * 
 * @typedef {{
 * 	view: TreeDOM
 * 	wifi: WifiInstance
 * 	connected: boolean
 * }} WifiView
 */

const app = {
	container: $("#app"),

	/** @type {TreeDOM} */
	view: undefined,

	/** @type {SQButton} */
	updateAvailableWifi: undefined,

	/** @type {LoadingOverlay} */
	loadingOverlay: undefined,

	/** @type {{ [mac: string]: WifiView }} */
	wifiViews: {},

	/** @type {WifiView} */
	currentConnected: undefined,

	init() {
		this.updateAvailableWifi = createButton("", {
			icon: "refresh",
			complex: true,
			style: "round",
			triangleStyle: "border",
			onClick: () => this.scanWifi()
		});

		this.view = makeTree("div", "device-setup-form", {
			heading: { tag: "div", class: "heading", child: {
				icon: { tag: "span", class: "material-symbols-outlined", text: "home_iot_device" },
				// pageTitle: { tag: "h1", text: "Cấu hình thiết bị" }
			}},

			panel: { tag: "div", class: "panel", child: {
				wifiGroup: { tag: "div", class: ["group", "wifi"], child: {
					label: { tag: "div", class: "label", child: {
						text: { tag: "div", class: "text", text: "Wi-Fi" }
					}},

					content: { tag: "div", class: "content", child: {
						connectedLabel: { tag: "div", class: "label", text: "Đã kết nối" },
						connected: { tag: "div", class: "connected" },

						availableLabel: { tag: "div", class: "label", child: {
							display: { tag: "span", class: "display", text: "Mạng sẵn có" },
							controls: { tag: "span", class: "controls", child: {
								update: this.updateAvailableWifi
							}}
						}},

						availables: { tag: "div", class: "availables", child: {
							inner: { tag: "div", class: "inner" }
						}}
					}}
				}}
			}},

			footer: { tag: "div", class: "footer", child: {

			}}
		});

		new Scrollable(this.view.panel.wifiGroup.content.availables, {
			content: this.view.panel.wifiGroup.content.availables.inner
		});

		this.loadingOverlay = new LoadingOverlay(this.view.panel);
		this.loading = true;
		this.container.appendChild(this.view);
		this.updateStatus();
		this.scanWifi();
	},

	set loading(loading) {
		this.loadingOverlay.loading = loading;
	},

	wifiStrengthIcon(rssi) {
		if (rssi <= -80)
			return "signal_wifi_0_bar";
		else if (rssi <= -70)
			return "network_wifi_1_bar";
		else if (rssi <= -60)
			return "network_wifi_2_bar";
		else if (rssi <= -50)
			return "network_wifi_3_bar";

		return "signal_wifi_4_bar";
	},

	async updateStatus() {
		this.loading = true;

		try {
			// const response = await myajax({
			// 	url: "/api/wifi/status",
			// 	method: "GET"
			// });

			const response = {
				"mac": "24:dc:c3:4a:fb:8c",
				"channel": 10,
				"ssid": "Oneclass New",
				"rssi": -54,
				"txpower": 19.5,
				"status": "GOT_IP"
			};

			const view = this.renderWifi(response);

			this.view.panel.wifiGroup.content.connectedLabel.style.display = null;
			this.view.panel.wifiGroup.content.connected.style.display = null;
			view.connected = true;
		} catch (e) {
			this.log("WARN", `app.updateStatus()`, e);
			this.view.panel.wifiGroup.content.connectedLabel.style.display = "none";
			this.view.panel.wifiGroup.content.connected.style.display = "none";
		}

		this.loading = false;
	},

	async scanWifi() {
		this.updateAvailableWifi.loading = true;

		try {
			// const response = await myajax({
			// 	url: "/api/wifi/scan",
			// 	method: "GET"
			// });

			const response = [{"channel": 2, "hidden": false, "ssid": "", "bssid": "e4:c3:2a:c9:18:1a", "rssi": -34, "security": "OPEN"}, {"channel": 2, "hidden": false, "ssid": "", "bssid": "e4:c3:2a:c9:18:ca", "rssi": -47, "security": "WPA2-PSK"}, {"channel": 6, "hidden": false, "ssid": "DIRECT-f6-HP M227f LaserJet", "bssid": "c2:b5:d7:d1:4b:f6", "rssi": -49, "security": "WPA2-PSK"}, {"channel": 5, "hidden": false, "ssid": "OneClass", "bssid": "c4:27:28:11:c6:94", "rssi": -53, "security": "WPA/WPA2-PSK"}, {"channel": 10, "hidden": false, "ssid": "Oneclass New", "bssid": "2c:70:4f:06:29:b0", "rssi": -56, "security": "WPA2-PSK"}, {"channel": 6, "hidden": false, "ssid": "DIRECT-9c-HP M236 LaserJet", "bssid": "ae:50:de:51:54:9c", "rssi": -64, "security": "WPA2-PSK"}, {"channel": 11, "hidden": false, "ssid": "SUNCT", "bssid": "60:22:32:a6:1d:c6", "rssi": -65, "security": "WPA2-PSK"}, {"channel": 7, "hidden": false, "ssid": "Oneclass New 1", "bssid": "2c:70:4f:05:d1:c8", "rssi": -67, "security": "WPA2-PSK"}, {"channel": 9, "hidden": false, "ssid": "The Human", "bssid": "a8:5e:45:89:31:20", "rssi": -68, "security": "WPA2-PSK"}, {"channel": 11, "hidden": false, "ssid": "", "bssid": "66:22:32:a6:1d:c6", "rssi": -68, "security": "WPA2-PSK"}, {"channel": 7, "hidden": false, "ssid": "Thuc Anh", "bssid": "38:d5:7a:3c:49:20", "rssi": -74, "security": "WPA/WPA2-PSK"}, {"channel": 1, "hidden": false, "ssid": "Doha Land", "bssid": "6c:f3:7f:65:f7:00", "rssi": -76, "security": "WPA2-PSK"}, {"channel": 1, "hidden": false, "ssid": "Doha Land", "bssid": "6c:f3:7f:5e:f0:00", "rssi": -78, "security": "WPA2-PSK"}, {"channel": 6, "hidden": false, "ssid": "P407", "bssid": "14:4d:67:32:e7:d4", "rssi": -79, "security": "WPA2-PSK"}, {"channel": 11, "hidden": false, "ssid": "Doha Land 2.4G", "bssid": "6c:f3:7f:60:8e:61", "rssi": -81, "security": "WPA2-PSK"}, {"channel": 11, "hidden": false, "ssid": "The_Human", "bssid": "84:d4:7e:f7:23:20", "rssi": -81, "security": "WPA2-PSK"}, {"channel": 11, "hidden": false, "ssid": "", "bssid": "e2:5d:54:5f:0d:db", "rssi": -84, "security": "WPA/WPA2-PSK"}, {"channel": 6, "hidden": false, "ssid": "Soc Soc_5G_plus", "bssid": "64:09:80:53:b7:9f", "rssi": -87, "security": "WPA/WPA2-PSK"}, {"channel": 11, "hidden": false, "ssid": "Doha Land", "bssid": "6c:f3:7f:61:8a:60", "rssi": -87, "security": "WPA2-PSK"}, {"channel": 1, "hidden": false, "ssid": "0804C", "bssid": "7c:a1:07:bb:3a:00", "rssi": -89, "security": "WPA/WPA2-PSK"}, {"channel": 1, "hidden": false, "ssid": "JapanshopVP", "bssid": "06:81:d4:0c:88:fb", "rssi": -91, "security": "WPA/WPA2-PSK"}, {"channel": 11, "hidden": false, "ssid": "Minh Phong", "bssid": "68:9e:29:98:ac:26", "rssi": -93, "security": "WPA/WPA2-PSK"}, {"channel": 9, "hidden": false, "ssid": "Hien Bi", "bssid": "50:c2:e8:1d:29:e0", "rssi": -94, "security": "WPA/WPA2-PSK"}, {"channel": 11, "hidden": false, "ssid": "C0707", "bssid": "60:59:47:e6:8b:80", "rssi": -94, "security": "WPA/WPA2-PSK"}, {"channel": 11, "hidden": false, "ssid": "A DI DA PHAT", "bssid": "5c:1a:6f:76:91:29", "rssi": -96, "security": "WPA/WPA2-PSK"}];

			emptyNode(this.view.panel.wifiGroup.content.availables.inner);

			for (const item of response) {
				const view = this.renderWifi(item);
				this.view.panel.wifiGroup.content.availables.inner.appendChild(view.view);
			}
		} catch (e) {
			this.log("WARN", `app.scanWifi()`, e);
		}

		this.updateAvailableWifi.loading = false;
	},

	renderWifi(/** @type {WifiInstance} */ wifi) {
		if (!this.wifiViews[wifi.bssid]) {
			const view = makeTree("div", "wifi-item", {
				strengh: { tag: "span", class: "material-symbols-outlined", text: "signal_wifi_4_bar" },

				info: { tag: "span", class: "info", child: {
					ssid: { tag: "div", class: "ssid", child: {
						display: { tag: "span", class: "display", text: "Sample Wifi" },
						badge: { tag: "span", class: "badge", text: "WPA2" }
					}},
	
					metas: { tag: "div", class: "metas" }
				}},

				lock: (wifi.security !== "OPEN")
					? { tag: "span", class: ["material-symbols-outlined", "lock"], text: "lock" }
					: null,

				action: { tag: "span", class: ["material-symbols-outlined", "action"], text: "chevron_right" },
			});

			let isConnected = false;

			const setConnected = (connected) => {
				if (isConnected === connected)
					return;

				if (connected) {
					if (this.currentConnected) {
						this.currentConnected.classList.remove("connected");
						this.view.panel.wifiGroup.content.availables.inner.appendChild(this.currentConnected.view);
					}

					this.view.panel.wifiGroup.content.connected.appendChild(view);
				}

				view.classList.toggle("connected", connected);
				isConnected = connected;

				if (connected)
					this.currentConnected = instance;
			};

			const instance = {
				view,
				wifi,

				set connected(connected) {
					setConnected(connected);
				},

				get connected() {
					return isConnected;
				}
			};

			this.wifiViews[wifi.bssid] = instance;
		}

		const instance = this.wifiViews[wifi.bssid];
		const { view } = instance;
		instance.wifi = Object.assign(instance.wifi, wifi);

		view.strengh.innerText = this.wifiStrengthIcon(wifi.rssi);
		view.info.ssid.display.innerText = wifi.ssid;

		if (wifi.security) {
			if (!view.info.ssid.contains(view.info.ssid.badge))
				view.info.ssid.appendChild(view.info.ssid.badge);

			view.info.ssid.badge.innerText = wifi.security;
		} else {
			if (view.info.ssid.contains(view.info.ssid.badge))
				view.info.ssid.removeChild(view.info.ssid.badge);
		}

		emptyNode(view.info.metas);

		if (wifi.status) {
			const node = document.createElement("span");
			node.classList.add("meta");
			node.innerText = {
				UNKNOWN: "Lỗi không rõ",
				IDLE: "Chưa kết nối",
				CONNECTING: "Đang kết nối...",
				WRONG_PASSWORD: "Mật khẩu không chính xác",
				GOT_IP: "Đã kết nối",
				NO_AP_FOUND: "Không tìm thấy điểm truy cập"
			}[wifi.status];
			view.info.metas.appendChild(node);

			const dot = document.createElement("dot");
			view.info.metas.appendChild(dot);
		}

		if (wifi.bssid) {
			const node = document.createElement("span");
			node.classList.add("meta");
			node.innerText = wifi.bssid;
			view.info.metas.appendChild(node);

			const dot = document.createElement("dot");
			view.info.metas.appendChild(dot);
		}

		if (wifi.mac) {
			const node = document.createElement("span");
			node.classList.add("meta");
			node.innerText = wifi.mac;
			view.info.metas.appendChild(node);

			const dot = document.createElement("dot");
			view.info.metas.appendChild(dot);
		}

		if (wifi.channel) {
			const node = document.createElement("span");
			node.classList.add("meta");
			node.innerText = `C${wifi.channel}`;
			view.info.metas.appendChild(node);

			const dot = document.createElement("dot");
			view.info.metas.appendChild(dot);
		}

		view.info.metas.removeChild(view.info.metas.lastChild);

		return instance;
	}
}

initGroup({ app }, "app");
