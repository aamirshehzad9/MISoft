import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../layout/Sidebar';
import Header from '../layout/Header';
import './MainLayout.css';

const MainLayout = () => {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (
        <div className="main-layout">
            <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
            <div className="main-layout-content">
                <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
                <main className="main-layout-body">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default MainLayout;
