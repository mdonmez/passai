class PassAI {
  #keyPair = null;
  #timeoutId = null;

  constructor() {
    this.initializeElements();
    this.setupEventListeners();
    this.setFavicon();
    this.generateKeyPair();
  }

  async generateKeyPair() {
    try {
      this.#keyPair = await crypto.subtle.generateKey(
        {
          name: "RSA-OAEP",
          modulusLength: 2048,
          publicExponent: new Uint8Array([1, 0, 1]),
          hash: "SHA-256",
        },
        true,
        ["encrypt", "decrypt"]
      );
      console.log("Encryption keys generated");
    } catch (err) {
      console.error("Failed to generate encryption keys:", err);
    }
  }

  async exportPublicKey() {
    try {
      const exported = await crypto.subtle.exportKey(
        "spki",
        this.#keyPair.publicKey
      );
      const exportedAsBase64 = this.#arrayBufferToBase64(exported);
      const pemExported = `-----BEGIN PUBLIC KEY-----\n${exportedAsBase64}\n-----END PUBLIC KEY-----`;
      return btoa(pemExported);
    } catch (err) {
      console.error("Failed to export public key:", err);
      throw err;
    }
  }

  async decryptPassword(encryptedBase64) {
    try {
      const encryptedData = this.#base64ToArrayBuffer(encryptedBase64);
      const decrypted = await crypto.subtle.decrypt(
        {
          name: "RSA-OAEP",
        },
        this.#keyPair.privateKey,
        encryptedData
      );
      return new TextDecoder().decode(decrypted);
    } catch (err) {
      console.error("Failed to decrypt password:", err);
      throw err;
    }
  }

  #arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = "";
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  #base64ToArrayBuffer(base64) {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
  }

  initializeElements() {
    this.userInput = document.getElementById("userInput");
    this.passDisplay = document.getElementById("passDisplay");
    this.passText = document.getElementById("passText");
    this.loading = document.getElementById("loading");
    this.error = document.getElementById("error");
    this.copiedToast = document.getElementById("copiedToast");
    this.favicon = document.getElementById("favicon");
  }

  setupEventListeners() {
    this.userInput.addEventListener("input", (event) => {
      this.handleUserInput(event);
    });

    window
      .matchMedia("(prefers-color-scheme: dark)")
      .addEventListener("change", () => this.setFavicon());
  }

  setFavicon() {
    const isDarkMode = window.matchMedia(
      "(prefers-color-scheme: dark)"
    ).matches;

    if (isDarkMode) {
      this.favicon.href = "/static/light_logo.svg";
    } else {
      this.favicon.href = "/static/dark_logo.svg";
    }
  }

  handleUserInput(event) {
    const textarea = event.target;
    clearTimeout(this.#timeoutId);

    this.#timeoutId = setTimeout(() => {
      this.generatePass(textarea.value);
    }, 1000);

    this.autoResizeTextarea(textarea);
  }

  autoResizeTextarea(textarea) {
    textarea.style.height = "auto";
    const maxHeight = window.innerWidth <= 640 ? 160 : 200;
    const newHeight = Math.min(textarea.scrollHeight, maxHeight);
    textarea.style.height = newHeight + "px";

    if (textarea.scrollHeight > maxHeight) {
      textarea.style.overflowY = "auto";
    } else {
      textarea.style.overflowY = "hidden";
    }
  }

  showError(message) {
    this.error.textContent = message;
    this.error.classList.add("show");
  }

  hideError() {
    this.error.classList.remove("show");
  }

  showLoading() {
    this.loading.classList.add("show");
    this.hideError();
    this.copiedToast.classList.remove("show");
  }

  hideLoading() {
    this.loading.classList.remove("show");
  }

  showCopiedIndicator() {
    this.copiedToast.classList.add("show");
    setTimeout(() => {
      this.copiedToast.classList.remove("show");
    }, 1500);
  }

  async copyToClipboard(text) {
    const activeElement = document.activeElement;

    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      console.warn("Clipboard API failed, using fallback:", err);
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
    }

    if (activeElement === this.userInput) {
      this.userInput.focus();
    }
  }

  async generatePass(input) {
    if (!input.trim()) {
      this.transitionToPlaceholder();
      this.hideLoading();
      this.hideError();
      return;
    }

    if (!this.#keyPair) {
      this.showError("Encryption not ready. Please wait and try again.");
      return;
    }

    this.showLoading();

    try {
      const publicKey = await this.exportPublicKey();

      const response = await fetch("/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          input,
          publicKey,
        }),
      });

      const data = await response.json();
      this.hideLoading();

      if (data.error) {
        this.showError(data.error);
        this.transitionToPlaceholder();
      } else if (data.encryptedPass) {
        const decryptedPass = await this.decryptPassword(data.encryptedPass);
        this.hideError();
        this.transitionToPass(decryptedPass);
        await this.copyToClipboard(decryptedPass);
        this.showCopiedIndicator();
      } else {
        this.showError("Invalid response from server.");
        this.transitionToPlaceholder();
      }
    } catch (err) {
      this.hideLoading();
      this.showError("Failed to generate pass. Please try again.");
      console.error("API Error:", err);
    }
  }

  transitionToPlaceholder() {
    if (this.passDisplay.classList.contains("empty")) {
      this.passText.textContent = "your pass will appear here";
      this.passText.classList.remove("hide", "show");
      return;
    }

    this.passDisplay.classList.add("transitioning");
    this.passText.classList.add("transitioning", "hide");
    this.passText.classList.remove("show");

    setTimeout(() => {
      this.passText.textContent = "your pass will appear here";
      this.passDisplay.classList.add("empty");
      this.passDisplay.classList.remove("transitioning");
      this.passText.classList.remove("transitioning", "hide");
    }, 250);
  }

  transitionToPass(pass) {
    const wasEmpty = this.passDisplay.classList.contains("empty");
    const delay = wasEmpty ? 150 : 250;

    this.passDisplay.classList.add("transitioning");
    this.passText.classList.add("transitioning", "hide");
    this.passText.classList.remove("show");

    setTimeout(() => {
      this.passText.textContent = pass;
      this.passDisplay.classList.remove("empty");
      this.passText.classList.remove("hide");
      this.passText.classList.add("show");

      setTimeout(() => {
        this.passDisplay.classList.remove("transitioning");
        this.passText.classList.remove("transitioning");
      }, 300);
    }, delay);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new PassAI();
});
