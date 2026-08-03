import axios from "axios";

export const baseApi = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});


console.log("BASE URL:", import.meta.env.VITE_API_BASE_URL);
console.log("AXIOS BASE:", baseApi.defaults.baseURL);
