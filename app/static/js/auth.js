// Firebase ile giriş (e-posta ve telefon). Projedeki tek JavaScript dosyası.
// Akış: Firebase giriş yapar -> ID token alınır -> POST /session -> sunucu doğrular.
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
    getAuth,
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    sendEmailVerification,
    RecaptchaVerifier,
    signInWithPhoneNumber,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

const box = document.getElementById("firebase-login");
const message = box.querySelector("[data-auth-message]");
const emailForm = box.querySelector("[data-email-form]");
const phoneForm = box.querySelector("[data-phone-form]");
const codeForm = box.querySelector("[data-code-form]");

const app = initializeApp(JSON.parse(box.dataset.config));
const auth = getAuth(app);
auth.languageCode = "tr"; // e-posta ve SMS Türkçe

// Firebase hata kodları -> Türkçe mesaj
const ERRORS = {
    "auth/invalid-credential": "E-posta ya da şifre yanlış.",
    "auth/invalid-email": "E-posta adresi geçersiz.",
    "auth/email-already-in-use": "Bu e-posta ile zaten kayıt olunmuş.",
    "auth/weak-password": "Şifre en az 6 karakter olmalı.",
    "auth/invalid-phone-number": "Telefon numarası geçersiz. Örnek: +905551112233",
    "auth/invalid-verification-code": "SMS kodu yanlış.",
    "auth/too-many-requests": "Çok fazla deneme yapıldı. Biraz sonra tekrar dene.",
};

function showMessage(text) {
    message.textContent = text;
}

function showError(error) {
    showMessage(ERRORS[error.code] || "Bir hata oldu, tekrar dene.");
}

// Token'ı sunucuya yollar, sonra geri döner
async function startSession(user) {
    const idToken = await user.getIdToken();
    const response = await fetch(box.dataset.sessionUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_token: idToken }),
    });
    if (response.ok) {
        window.location.href = box.dataset.next;
    } else {
        showMessage("Giriş başarısız.");
    }
}

// E-posta: giriş ya da kayıt
emailForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = emailForm.email.value;
    const password = emailForm.password.value;
    try {
        if (event.submitter.value === "register") {
            const result = await createUserWithEmailAndPassword(auth, email, password);
            await sendEmailVerification(result.user);
            showMessage("Doğrulama e-postası gönderildi. Linke tıkladıktan sonra giriş yap.");
            return;
        }
        const result = await signInWithEmailAndPassword(auth, email, password);
        // Doğrulanmamış e-posta ile oturum açılmaz
        if (!result.user.emailVerified) {
            await sendEmailVerification(result.user);
            showMessage("E-postan doğrulanmamış. Yeni doğrulama e-postası gönderildi.");
            return;
        }
        await startSession(result.user);
    } catch (error) {
        showError(error);
    }
});

// Telefon: önce SMS kodu gönderilir
let confirmation = null;
const recaptcha = new RecaptchaVerifier(auth, "recaptcha", { size: "invisible" });

phoneForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
        confirmation = await signInWithPhoneNumber(auth, phoneForm.phone.value, recaptcha);
        codeForm.hidden = false;
        showMessage("SMS kodu gönderildi.");
    } catch (error) {
        showError(error);
    }
});

// Telefon: gelen kod doğrulanır
codeForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
        const result = await confirmation.confirm(codeForm.code.value);
        await startSession(result.user);
    } catch (error) {
        showError(error);
    }
});
