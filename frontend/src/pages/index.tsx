import Head from 'next/head';
import Header from '../components/Header';
import '../styles/global.css';

export default function Home() {
  return (
    <div>
      <Head>
        <title>COVID Digital Twin Dashboard</title>
      </Head>
      <Header />
      <main>
        <h1>Welcome to the COVID Digital Twin</h1>
        <p>
          Explore simulation scenarios and view realistic citizen behaviors in our digital twin of Los Angeles.
        </p>
        <p>
          <a href="/simulation">Run Simulation</a>
        </p>
      </main>
    </div>
  );
}
