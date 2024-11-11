
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
 * 	status: ?string
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
		popup.init();

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

	async updateStatus(continuous = false) {
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

				continuous = false;
			} else if (response.status === "GOT_IP") {
				const view = this.renderWifi(response);
	
				this.view.panel.wifiGroup.content.connectedLabel.style.display = null;
				this.view.panel.wifiGroup.content.connected.style.display = null;
				view.connected = true;
				continuous = false;
			} else if (this.currentConnected) {
				const view = this.renderWifi(this.currentConnected, false);
				view.status = {
					"CONNECTING": "Đang kết nối...",
					"WRONG_PASSWORD": "Sai mật khẩu!",
					"NO_AP_FOUND": "Không tìm thấy điểm truy cập!"
				};

				continuous = (view.status === "CONNECTING");
			}
		} catch (e) {
			this.log("WARN", `app.updateStatus()`, e);
			this.view.panel.wifiGroup.content.connectedLabel.style.display = "none";
			this.view.panel.wifiGroup.content.connected.style.display = "none";

			if (this.currentConnected)
				this.currentConnected.connected = false;
		}

		if (continuous) {
			await delayAsync(500);
			this.updateStatus(continuous);
		}
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

	renderWifi(/** @type {WifiInstance} */ wifi, update = true) {
		if (!this.wifiViews[wifi.bssid]) {
			const view = makeTree("div", "wifi-item", {
				strengh: { tag: "span", class: "material-symbols", text: "signal_wifi_4_bar" },

				info: { tag: "span", class: "info", child: {
					ssid: { tag: "div", class: "ssid", child: {
						display: { tag: "span", class: "display", text: "Sample Wifi" },
						badge: { tag: "span", class: "badge", text: "WPA2" }
					}},
	
					metas: { tag: "div", class: "metas" },
					status: { tag: "div", class: "status" }
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

				const conn = this.view.panel.wifiGroup.content.connected;
				const avail = this.view.panel.wifiGroup.content.availables.inner;

				if (connected) {
					if (this.currentConnected) {
						this.currentConnected.view.classList.remove("connected");
						avail.insertBefore(this.currentConnected.view, avail.firstChild);
					}

					conn.insertBefore(view, conn.firstChild);
					this.currentConnected = instance;

					this.view.panel.wifiGroup.content.connectedLabel.style.display = null;
					conn.style.display = null;
				} else {
					this.view.panel.wifiGroup.content.connectedLabel.style.display = "none";
					conn.style.display = "none";
					avail.insertBefore(view, avail.firstChild);
				}

				view.classList.toggle("connected", connected);
				isConnected = connected;
			};

			const setStatus = (status) => {
				if (!status) {
					if (view.info.contains(view.info.status))
						view.info.removeChild(view.info.status);
				} else {
					view.info.status.innerText = status;

					if (!view.info.contains(view.info.status))
						view.info.appendChild(view.info.status);
				}
			};

			const instance = {
				view,
				wifi,

				set connected(connected) {
					setConnected(connected);
				},

				get connected() {
					return isConnected;
				},

				set status(status) {
					setStatus(status);
				}
			};

			view.addEventListener("click", () => this.connectWifi(instance.wifi));
			this.wifiViews[wifi.bssid] = instance;
		}

		if (!update)
			return this.wifiViews[wifi.bssid];

		const instance = this.wifiViews[wifi.bssid];
		const { view } = instance;

		for (const [key, value] of Object.entries(wifi))
			instance.wifi[key] = value;

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
	},

	async connectWifi(/** @type {WifiInstance} */ instance) {
		let password = null;

		if (instance.security !== "OPEN") {
			let input = createInput({
				type: "text",
				label: "Mật khẩu",
				autofill: false,
				animated: true
			});

			input.group.style.marginTop = "0.5rem";
			input.input.addEventListener("input", () => {
				popup.buttons.confirm.disabled = !input.value;
			});

			setTimeout(() => {
				input.group.classList.add("show");
				popup.buttons.confirm.disabled = true;

				setTimeout(() => {
					input.input.focus();
				}, 200);
			}, 10);

			const action = await popup.show({
				windowTitle: "Wi-Fi",
				title: `Kết nối`,
				message: `Nhập mật khẩu để kết nối vào mạng <strong>${instance.ssid}</strong>`,
				customNode: input.group,
				bgColor: "accent",
				buttons: {
					cancel: {
						text: "Hủy",
						color: "pink"
					},

					confirm: {
						text: "Kết Nối",
						color: "accent"
					}
				}
			});

			if (action !== "confirm")
				return;

			password = input.value;
		}

		this.log("INFO", `Attempting to connect to wifi ${instance.ssid} with password ${password}`);
		const view = this.renderWifi(instance, false);

		view.connected = true;
		view.view.classList.add("connecting");
		view.status = "Đang kết nối...";

		try {
			this.updateStatus(true);

			await myajax({
				url: `/api/wifi/connect`,
				method: "POST",
				query: { ssid: instance.ssid, password }
			});
		} catch (e) {
			view.connected = false;
			view.view.classList.remove("connecting");
			view.status = "Kết nối thất bại";
		}
	}
}

window.addEventListener("load", () => initGroup({ app }, "app"));
