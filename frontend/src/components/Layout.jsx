import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';

const Layout = () => {
    return (
        <div className="min-h-screen bg-slate-950 text-white selection:bg-blue-500/30">
            {/* Background elements */}
            <div className="fixed top-0 left-0 w-full h-full pointer-events-none overflow-hidden z-0">
                <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-purple-900/20 rounded-full blur-3xl opacity-50"></div>
                <div className="absolute bottom-[-10%] left-[20%] w-[400px] h-[400px] bg-blue-900/20 rounded-full blur-3xl opacity-50"></div>
            </div>

            <Sidebar />

            <div className="relative z-10">
                <Header />

                {/* Main Content Area */}
                {/* ml-64 for sidebar offset, pt-28 for header offset + gap (7rem) */}
                <main className="ml-64 pt-28 px-8 pb-8 min-h-screen">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default Layout;
