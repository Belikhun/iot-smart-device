
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

	/** @type {{ [name: string]: Blob }} */
	icons: {},

	async init() {
		this.updateAvailableWifi = createButton("", {
			icon: "refresh",
			complex: true,
			style: "round",
			triangleStyle: "border",
			onClick: () => this.scanWifi()
		});

		this.view = makeTree("div", "device-setup-form", {
			heading: { tag: "div", class: "heading", child: {
				icon: { tag: "span", class: "material-symbols", text: "home_iot_device" },
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

		this.view.panel.wifiGroup.content.connectedLabel.style.display = "none";
		this.view.panel.wifiGroup.content.connected.style.display = "none";

		new Scrollable(this.view.panel.wifiGroup.content.availables, {
			content: this.view.panel.wifiGroup.content.availables.inner
		});

		this.loadingOverlay = new LoadingOverlay(this.view.panel);
		this.container.appendChild(this.view);

		await this.updateStatus();
		this.scanWifi();

		const appLoading = new LoadingOverlay();
		appLoading.container = $("#app-loading");
		appLoading.spinner = $("#app-loading > .spinner");
		appLoading.isLoading = true;
		appLoading.loading = false;
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
		// this.loading = true;

		try {
			const response = await myajax({
				url: "/api/wifi/status",
				method: "GET"
			});

			if (response.status === "IDLE") {
				this.view.panel.wifiGroup.content.connectedLabel.style.display = "none";
				this.view.panel.wifiGroup.content.connected.style.display = "none";

				if (this.currentConnected)
					this.currentConnected.connected = false;
			} else {
				const view = this.renderWifi(response);
	
				this.view.panel.wifiGroup.content.connectedLabel.style.display = null;
				this.view.panel.wifiGroup.content.connected.style.display = null;
				view.connected = true;
			}
		} catch (e) {
			this.log("WARN", `app.updateStatus()`, e);
			this.view.panel.wifiGroup.content.connectedLabel.style.display = "none";
			this.view.panel.wifiGroup.content.connected.style.display = "none";

			if (this.currentConnected)
				this.currentConnected.connected = false;
		}

		// this.loading = false;
	},

	async scanWifi() {
		this.updateAvailableWifi.loading = true;

		try {
			const response = await myajax({
				url: "/api/wifi/scan",
				method: "GET"
			});

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
				strengh: { tag: "span", class: "material-symbols", text: "signal_wifi_4_bar" },

				info: { tag: "span", class: "info", child: {
					ssid: { tag: "div", class: "ssid", child: {
						display: { tag: "span", class: "display", text: "Sample Wifi" },
						badge: { tag: "span", class: "badge", text: "WPA2" }
					}},
	
					metas: { tag: "div", class: "metas" }
				}},

				lock: (wifi.security !== "OPEN")
					? { tag: "span", class: ["material-symbols", "lock"], text: "lock" }
					: null,

				action: { tag: "span", class: ["material-symbols", "action"], text: "chevron_right" },
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

window.addEventListener("load", () => initGroup({ app }, "app"));
