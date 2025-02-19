import Head from 'next/head';
import Header from '../components/Header';
import '../styles/global.css';

export default function Dashboard() {
    return (
        <div>
            <Head>
                <title>Dashboard</title>
            </Head>
            <Header />
            <main style={{ padding: "1rem" }}>
                <h1>Dashboard</h1>
                <p>This dashboard will display additional metrics and insights over time.</p>
            </main>
        </div>
    );
}
