import axios from "axios";
import { API_BASE } from "../config";

const authHeaders = () => ({ Authorization: `Bearer ${localStorage.getItem("resumeiq-token")}` });

export async function getAnalysisTotal(signal) {
  return (await axios.get(`${API_BASE}/stats/analyses`, { signal, timeout: 10000 })).data;
}

export async function getAnalysisHistory(offset, signal) {
  return (await axios.get(`${API_BASE}/resume/history`, {
    params: { offset, limit: 10 }, headers: authHeaders(), signal, timeout: 15000,
  })).data;
}

export async function getSavedAnalysis(id, signal) {
  return (await axios.get(`${API_BASE}/resume/history/${id}`, {
    headers: authHeaders(), signal, timeout: 15000,
  })).data;
}
