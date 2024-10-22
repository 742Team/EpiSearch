import { initializeApp } from 'firebase/app';
import { getFirestore, collection, addDoc, getDocs, query, where } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "your-api-key",
  authDomain: "your-auth-domain",
  projectId: "your-project-id",
  storageBucket: "your-storage-bucket",
  messagingSenderId: "your-messaging-sender-id",
  appId: "your-app-id"
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
