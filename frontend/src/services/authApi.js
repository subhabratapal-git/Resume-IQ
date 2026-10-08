import axios from "axios";
import { API_BASE } from "../config";


export const registerUser = async (userData) => {
  const response = await axios.post(
    `${API_BASE}/auth/register`,
    userData
  );

  return response.data;
};


export const loginUser = async (loginData) => {
  const response = await axios.post(
    `${API_BASE}/auth/login`,
    loginData
  );

  return response.data;
};


export const getCurrentUser = async () => {
  const token = localStorage.getItem("resumeiq-token");

  const response = await axios.get(
    `${API_BASE}/auth/me`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};


export const saveAuth = (data) => {
  localStorage.setItem(
    "resumeiq-token",
    data.access_token
  );

  localStorage.setItem(
    "resumeiq-user",
    JSON.stringify(data.user)
  );
};


export const logoutUser = () => {
  localStorage.removeItem("resumeiq-token");
  localStorage.removeItem("resumeiq-user");
};


export const changePassword = async (passwordData) => {
  const token = localStorage.getItem("resumeiq-token");

  const response = await axios.post(
    `${API_BASE}/auth/change-password`,
    passwordData,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};


