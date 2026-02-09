import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useState } from "react";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Feed from "./pages/Feed";
import ItemDetail from "./pages/ItemDetail";
import Home from "./pages/Home";
import UserProfile from "./pages/UserProfile";
import EditProfile from "./pages/EditProfile";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import VerifyResetCode from "./pages/VerifyResetCode";
import SetNewPassword from "./pages/SetNewPassword";   
import ListDetail from "./pages/ListDetail";
import Navbar from "./components/Navbar";
import UnauthorizedModal from "./components/UnauthorizedModal";
import { ToastProvider } from "./components/Toast";

export default function App() {
  const [authModal, setAuthModal] = useState(false);

  // 401 olduğunda API interceptor bunu çağıracak
  window.showAuthModal = () => setAuthModal(true);

  return (
    <ToastProvider>
      <BrowserRouter>

        {/* === GLOBAL 401 MODAL === */}
        <UnauthorizedModal
          show={authModal}
          onClose={() => setAuthModal(false)}
        />

        {/* === NAVBAR === */}
        <Navbar />

        {/* ROUTES */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/feed" element={<Feed />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/verify-code" element={<VerifyResetCode />} />
          <Route path="/set-new-password" element={<SetNewPassword />} />
          <Route path="/lists/:id" element={<ListDetail />} />


          {/* PROFİL ROUTES */}
          <Route path="/user/:id" element={<UserProfile />} />  
          <Route path="/profile/:id" element={<UserProfile />} />  
          <Route path="/me" element={<UserProfile />} />

          <Route path="/item/:id" element={<ItemDetail />} />
          <Route path="/edit-profile" element={<EditProfile />} />
        </Routes>


      </BrowserRouter>
    </ToastProvider>
  );
}
