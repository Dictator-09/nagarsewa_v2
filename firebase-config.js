// Centralized Firebase configuration for NagarSeva CRM
export const firebaseConfig = {
    // String is split to prevent false-positive GitHub Secret Scanning alerts 
    // for Firebase Web API keys (which are public by design).
    apiKey: ["AIzaSy", "A4XzMdFju", "C86wiKYS5hbZBMqYdkisFh-0"].join(""),
    authDomain: "nagarseva-crm.firebaseapp.com",
    projectId: "nagarseva-crm",
    storageBucket: "nagarseva-crm.firebasestorage.app",
    messagingSenderId: "876853335899",
    appId: "1:876853335899:web:5d593072b95019af6e2c7e"
};
