DEBUG = true;

/**
 * @typedef {{
 *	channel: number
 *	hidden: boolean
 *	ssid: string
 *	bssid: string
 *	mac: string
 *	rssi: number
 *	address: string
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

	serverInput: undefined,

	/** @type {SQButton} */
	serverUpdateButton: undefined,

	/** @type {SQButton} */
	logUpdateButton: undefined,

	/** @type {TreeDOM} */
	logViewer: undefined,

	/** @type {Scrollable} */
	logScroll: undefined,

	hwid: null,
	name: null,
	isConnecting: false,
	currentServer: "",
	logIndex: 0,

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

		this.serverInput = createOscInput({
			type: "text",
			label: "Địa chỉ",
			value: "",
			onInput: (value) => {
				this.serverUpdateButton.disabled = !(value && value != this.currentServer && this.currentConnected);
			}
		});

		this.serverUpdateButton = createButton("", {
			icon: "chevron_right",
			color: "accent",
			onClick: () => this.connectServer()
		});

		this.logUpdateButton = createButton("", {
			icon: "refresh",
			color: "accent",
			onClick: () => this.updateLogs()
		});

		this.logViewer = document.createElement("div");
		this.logViewer.classList.add("log-viewer");

		this.view = makeTree("div", "device-setup-form", {
			heading: { tag: "div", class: "heading", child: {
				icon: { tag: "span", class: "material-symbols", text: "home_iot_device" },
				// pageTitle: { tag: "h1", text: "Cấu hình thiết bị" }
			}},

			panel: { tag: "div", class: "panel", child: {
				wifiGroup: { tag: "div", class: ["group", "wifi"], child: {
					label: { tag: "div", class: "label", child: {
						text: { tag: "div", class: "text", text: "Kết nối Wi-Fi" }
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
				}},

				serverGroup: { tag: "div", class: ["group", "server"], child: {
					label: { tag: "div", class: "label", child: {
						text: { tag: "div", class: "text", text: "Máy chủ" }
					}},

					content: { tag: "div", class: "content", child: {
						form: { tag: "div", class: "server-form", child: {
							input: this.serverInput,
							button: this.serverUpdateButton
						}},

						status: { tag: "div", class: "status", text: "Đang kiểm tra..." }
					}}
				}},

				logsGroup: { tag: "div", class: ["group", "logs"], child: {
					label: { tag: "div", class: "label", child: {
						text: { tag: "div", class: "text", text: "Nhật kí" },
						button: this.logUpdateButton
					}},

					content: { tag: "div", class: "content", child: {
						viewer: this.logViewer
					}}
				}}
			}},

			footer: { tag: "div", class: "footer", child: {
				devName: { tag: "span", class: "name", text: "Thiết Bị" },
				dot: { tag: "dot" },
				hwid: { tag: "span", class: "hwid", text: "HWID" },
				dot2: { tag: "dot" },
				author: { tag: "span", class: "author", text: "© Belikhun" },
			}}
		});

		this.view.panel.wifiGroup.content.connectedLabel.style.display = "none";
		this.view.panel.wifiGroup.content.connected.style.display = "none";

		new Scrollable(this.view.panel.wifiGroup.content.availables, {
			content: this.view.panel.wifiGroup.content.availables.inner
		});

		this.logScroll = new Scrollable(this.view.panel.logsGroup.content, {
			content: this.logViewer
		});

		this.loadingOverlay = new LoadingOverlay(this.view.panel);
		this.container.appendChild(this.view);

		new Scrollable(this.container, {
			content: this.view
		});

		await Promise.all([
			this.updateInfo(),
			this.updateStatus()
		]);

		this.scanWifi();
		this.updateServerStatus();
		this.startUpdateLogs();

		const appLoading = new LoadingOverlay();
		appLoading.container = $("#app-loading");
		appLoading.spinner = $("#app-loading > .spinner");
		appLoading.isLoading = true;
		appLoading.loading = false;
	},

	set loading(loading) {
		this.loadingOverlay.loading = loading;
	},

	async updateInfo() {
		try {
			const { hwid, name } = await myajax({
				url: "/api/info",
				method: "GET"
			});

			this.hwid = hwid;
			this.name = name;

			this.view.footer.devName.innerText = this.name;
			this.view.footer.hwid.innerText = this.hwid;
		} catch (e) {
			this.log("WARN", `Fetch device info failed:`, e);
		}
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

			this.log("DEBG", `Got current connection status: ${response.status}`);

			if (response.status === "IDLE") {
				// Discard idle status while connecting.
				if (this.isConnecting) {
					if (continuous)
						this.updateStatus(continuous);

					return;
				}

				this.view.panel.wifiGroup.content.connectedLabel.style.display = "none";
				this.view.panel.wifiGroup.content.connected.style.display = "none";

				if (this.currentConnected)
					this.currentConnected.connected = false;

				continuous = false;
				this.serverUpdateButton.disabled = true;
			} else if (response.status === "GOT_IP") {
				const view = this.renderWifi(response);

				this.view.panel.wifiGroup.content.connectedLabel.style.display = null;
				this.view.panel.wifiGroup.content.connected.style.display = null;
				view.connected = true;
				view.status = "Đã kết nối";
				view.view.classList.remove("connecting");
				continuous = false;
				this.serverUpdateButton.disabled = false;
			} else if (this.currentConnected) {
				const view = this.renderWifi(this.currentConnected.wifi, false);
				view.status = {
					"CONNECTING": "Đang kết nối...",
					"WRONG_PASSWORD": "Sai mật khẩu!",
					"NO_AP_FOUND": "Không tìm thấy điểm truy cập!",
					"GOT_IP": "Đã kết nối"
				}[response.status];

				if (response.status !== "CONNECTING" && response.status !== "GOT_IP") {
					this.log("WARN", `Connection failed. Reason: ${response.status}`);
					view.view.classList.remove("connecting");
					continuous = false;
				}

				this.serverUpdateButton.disabled = true;
			} else {
				continuous = false;
			}
		} catch (e) {
			this.log("WARN", `app.updateStatus()`, e);
			this.view.panel.wifiGroup.content.connectedLabel.style.display = "none";
			this.view.panel.wifiGroup.content.connected.style.display = "none";

			if (this.currentConnected)
				this.currentConnected.connected = false;
		}

		if (continuous)
			this.updateStatus(continuous);
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

				if (!view.connected)
					this.view.panel.wifiGroup.content.availables.inner.appendChild(view.view);
			}
		} catch (e) {
			this.log("WARN", `app.scanWifi()`, e);
		}

		this.updateAvailableWifi.loading = false;
	},

	renderWifi(/** @type {WifiInstance} */ wifi, update = true) {
		if (!this.wifiViews[wifi.ssid]) {
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
					if (this.currentConnected && this.currentConnected.wifi.ssid !== wifi.ssid)
						this.currentConnected.connected = false;

					conn.insertBefore(view, conn.firstChild);
					this.currentConnected = instance;
					this.view.panel.wifiGroup.content.connectedLabel.style.display = null;
					this.view.panel.wifiGroup.content.connected.style.display = null;
				} else {
					avail.insertBefore(view, avail.firstChild);

					// Clear connected status.
					if (instance.wifi.address) {
						instance.status = null;
						instance.wifi.address = null;
					}

					this.currentConnected = null;
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
			this.wifiViews[wifi.ssid] = instance;
		}

		if (!update)
			return this.wifiViews[wifi.ssid];

		const instance = this.wifiViews[wifi.ssid];
		const { view } = instance;

		for (const [key, value] of Object.entries(wifi))
			instance.wifi[key] = value;

		wifi = instance.wifi;
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
			instance.status = {
				UNKNOWN: "Lỗi không rõ",
				IDLE: "Chưa kết nối",
				CONNECTING: "Đang kết nối...",
				WRONG_PASSWORD: "Mật khẩu không chính xác",
				GOT_IP: "Đã kết nối",
				NO_AP_FOUND: "Không tìm thấy điểm truy cập"
			}[wifi.status];
		} else {
			instance.status = null;
		}

		if (wifi.address) {
			const node = document.createElement("span");
			node.classList.add("meta");
			node.innerText = wifi.address;
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

		instance.address = null;
		const view = this.renderWifi(instance);

		view.connected = true;
		view.view.classList.add("connecting");
		view.status = "Đang kết nối...";
		this.isConnecting = true;

		try {
			setTimeout(() => this.updateStatus(true), 1000);

			const { success, status } = await myajax({
				url: `/api/wifi/connect`,
				method: "GET",
				query: { ssid: instance.ssid, password }
			});

			this.log("INFO", `Connection task completed. Status: ${status}`);
			view.wifi.status = status;
			this.renderWifi(view.wifi);

			if (!success)
				throw new Error("Kết nối thất bại");
		} catch (e) {
			this.log("WARN", `connectWifi(${instance.ssid}) failed:`, e)
			view.connected = false;
			this.view.panel.wifiGroup.content.connectedLabel.style.display = "none";
			this.view.panel.wifiGroup.content.connected.style.display = "none";

			if (!view.wifi.status)
				view.status = "Lỗi hệ thống";
		}

		view.view.classList.remove("connecting");
		this.isConnecting = false;
	},

	async updateServerStatus() {
		this.serverUpdateButton.loading = true;
		const statNode = this.view.panel.serverGroup.content.status;

		try {
			const { server, connected } = await myajax({
				url: "/api/server/status",
				method: "GET"
			});

			this.serverInput.value = server;
			this.currentServer = (server) ? server : "";

			if (connected) {
				statNode.dataset.status = "connected";
				statNode.innerText = "Đã kết nối tới máy chủ";
			} else {
				statNode.dataset.status = "failed";
				statNode.innerText = "Chưa kết nối tới máy chủ";
			}
		} catch (e) {
			this.log("WARN", `Update server connection status failed:`, e);
			statNode.dataset.status = "failed";
			statNode.innerText = "Lỗi khi lấy trạng thái kết nối";
		}

		this.serverUpdateButton.loading = false;
		this.serverUpdateButton.disabled = !this.currentConnected;
	},

	async connectServer() {
		if (!this.currentConnected)
			return;

		this.serverUpdateButton.loading = true;
		const statNode = this.view.panel.serverGroup.content.status;

		try {
			statNode.dataset.status = "connecting";
			statNode.innerText = "Đang kết nối tới máy chủ...";

			const { connected } = await myajax({
				url: "/api/server/connect",
				method: "GET",
				query: { server: this.serverInput.value }
			});

			if (connected) {
				statNode.dataset.status = "connected";
				statNode.innerText = "Đã kết nối tới máy chủ";
			} else {
				statNode.dataset.status = "failed";
				statNode.innerText = "Không thể kết nối tới máy chủ";
			}
		} catch(e) {
			this.log("WARN", `Connect to server failed:`, e);
			statNode.dataset.status = "failed";
			statNode.innerText = "Lỗi khi kết nối tới máy chủ";
		}

		this.serverUpdateButton.loading = false;
	},

	async updateLogs() {
		this.logUpdateButton.loading = true;

		try {
			const logs = await myajax({
				url: "/api/logs",
				method: "GET",
				query: { index: this.logIndex }
			});

			for (const line of logs) {
				const node = document.createElement("div");
				node.innerText = line;
				this.logViewer.appendChild(node);
			}

			this.logIndex += logs.length;

			await nextFrameAsync();
			await nextFrameAsync();
			this.logScroll.toBottom();
		} catch(e) {
			this.log("WARN", `Failed while trying to fetch logs:`, e);
		}

		this.logUpdateButton.loading = false;
	},

	async startUpdateLogs() {
		const start = performance.now();
		await this.updateLogs();
		setTimeout(() => this.startUpdateLogs(), 2000 - (performance.now() - start));
	}
}

window.addEventListener("load", () => initGroup({ app }, "app"));
