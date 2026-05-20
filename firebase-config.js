// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyD9DdWpxv8OKmF6hpuNwDlLlfpbOx3riAE",
  authDomain: "financial-asistent.firebaseapp.com",
  projectId: "financial-asistent",
  storageBucket: "financial-asistent.firebasestorage.app",
  messagingSenderId: "702605526775",
  appId: "1:702605526775:web:150d4038df8aa053dfb5f2",
  measurementId: "G-H10XED4219"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);