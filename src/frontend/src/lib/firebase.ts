import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged } from "firebase/auth";

const config = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID,
};

let firebaseEnabled = false;

export function getFirebaseApp() {
  if (!config.apiKey) return null;
  firebaseEnabled = true;
  const app = getApps().length ? getApp() : initializeApp(config);

  // analytics는 브라우저 + measurementId 둘 다 있을 때만 lazy init.
  if (typeof window !== "undefined" && config.measurementId) {
    void import("firebase/analytics")
      .then(({ getAnalytics, isSupported }) =>
        isSupported().then((ok) => {
          if (ok) getAnalytics(app);
        })
      )
      .catch(() => {});
  }
  return app;
}

export function getFirebaseAuth() {
  const app = getFirebaseApp();
  return app ? getAuth(app) : null;
}

export async function signInWithGoogle() {
  const auth = getFirebaseAuth();
  if (!auth) return null;
  const result = await signInWithPopup(auth, new GoogleAuthProvider());
  const token = await result.user.getIdToken();
  window.localStorage.setItem("authToken", token);
  return result.user;
}

export async function signOutAndClear() {
  const auth = getFirebaseAuth();
  if (auth) await signOut(auth);
  window.localStorage.removeItem("authToken");
}

export function watchAuth(callback: (uid: string | null) => void) {
  const auth = getFirebaseAuth();
  if (!auth) return () => {};
  return onAuthStateChanged(auth, async (user) => {
    if (user) {
      const token = await user.getIdToken();
      window.localStorage.setItem("authToken", token);
      callback(user.uid);
    } else {
      window.localStorage.removeItem("authToken");
      callback(null);
    }
  });
}

export function isFirebaseEnabled() {
  return firebaseEnabled || Boolean(config.apiKey);
}
