import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import {
  getCurrentUser,
  logoutUser,
} from "../services/authApi";


function ProtectedRoute({ children }) {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    const verifyUser = async () => {
      const token = localStorage.getItem("resumeiq-token");

      if (!token) {
        setStatus("unauthorized");
        return;
      }

      try {
        const user = await getCurrentUser();

        localStorage.setItem(
          "resumeiq-user",
          JSON.stringify(user)
        );

        setStatus("authorized");
      } catch {
        logoutUser();
        setStatus("unauthorized");
      }
    };

    verifyUser();
  }, []);


  if (status === "checking") {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "grid",
          placeItems: "center",
          background: "#02040a",
          color: "#ffffff",
          fontFamily: "Inter, sans-serif",
          fontSize: "16px",
        }}
      >
        Checking ResumeIQ session...
      </div>
    );
  }


  if (status === "unauthorized") {
    return <Navigate to="/" replace />;
  }


  return children;
}

export default ProtectedRoute;


