import { initializeApp } from 'firebase/app';
import { getFirestore, collection, addDoc, getDocs, query, where } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "AIzaSyAzLeoEtJIFLQ66Xnqd4-mGftkmZR90dVc",
  authDomain: "chat-3d13c.firebaseapp.com",
  databaseURL: "https://chat-3d13c-default-rtdb.europe-west1.firebasedatabase.app",
  projectId: "chat-3d13c",
  storageBucket: "chat-3d13c.appspot.com",
  messagingSenderId: "827613007033",
  appId: "1:827613007033:web:fb8574026f3e70ae501f68"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

export async function storePage(url, content) {
  try {
    const docRef = await addDoc(collection(db, 'pages'), {
      url: url,
      content: content
    });
  } catch (e) {}
}

export async function getAllPages() {
  const querySnapshot = await getDocs(collection(db, 'pages'));
  let pages = [];
  querySnapshot.forEach((doc) => {
    pages.push({ url: doc.data().url, content: doc.data().content });
  });
  return pages;
}

export async function getPageByContent(searchTerm) {
  const q = query(collection(db, 'pages'), where('content', '>=', searchTerm), where('content', '<=', searchTerm + '\uf8ff'));
  const querySnapshot = await getDocs(q);
  let results = [];
  querySnapshot.forEach((doc) => {
    results.push({ url: doc.data().url, content: doc.data().content });
  });
  return results;
}
