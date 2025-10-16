// import axios from "axios";
// const BASE_URL = "http://localhost:8000";

// export const determineIndustry = async (customer) =>
//   axios.post(`${BASE_URL}/determine_industry`, { customer });

// export const getPortfolioSummary = async (payload) =>
//   axios.post(`${BASE_URL}/portfolio_summary`, payload);

// export const getPortfolioSummarySelected = async (payload) =>
//   axios.post(`${BASE_URL}/portfolio_summary_selected`, payload);

// export const generatePitch = async (payload) =>
//   axios.post(`${BASE_URL}/generate_pitch`, payload);

// export const chatWithAssistant = async (payload) =>
//   axios.post(`${BASE_URL}/chat`, payload);



import axios from "axios";

const API_BASE = "http://localhost:8000";

export async function determineIndustry(customer) {
  try {
    console.log("[API] Calling /determine_industry with:", customer);
    const response = await axios.post(`${API_BASE}/determine_industry`, { customer });
    console.log("[API] /determine_industry response:", response.data);
    // Backend returns {"data": {"industry": "...", "confidence": 0.8}}
    return response.data.data || response.data; // Handle both formats
  } catch (error) {
    console.error("[API] /determine_industry error:", error);
    throw error;
  }
}

export async function getPortfolioSummary(params) {
  try {
    console.log("[API] Calling /portfolio_summary with:", params);
    const response = await axios.post(`${API_BASE}/portfolio_summary`, params);
    console.log("[API] /portfolio_summary response:", response.data);
    return response.data; // Return the actual data
  } catch (error) {
    console.error("[API] /portfolio_summary error:", error);
    throw error;
  }
}

export async function getPortfolioSummarySelected(params) {
  try {
    console.log("[API] Calling /portfolio_summary_selected with:", params);
    const response = await axios.post(`${API_BASE}/portfolio_summary_selected`, params);
    console.log("[API] /portfolio_summary_selected response:", response.data);
    return response.data; // Return the actual data
  } catch (error) {
    console.error("[API] /portfolio_summary_selected error:", error);
    throw error;
  }
}

export async function getCaseStudySummary(params) {
  return axios.post(`${API_BASE}/generate_pitch`, params);
}

export async function chatWithAssistant(params) {
  return axios.post(`${API_BASE}/chat`, params);
}

export async function refinePitch(params) {
  return axios.post(`${API_BASE}/refine_pitch`, params);
}