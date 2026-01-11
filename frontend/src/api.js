import axios from "axios";

const API_BASE_URL = "https://wiki-quiz-backend-rev4.onrender.com";

export const generateQuiz = async (url) => {
  const response = await axios.post(`${API_BASE_URL}/api/generate-quiz`, {
    url,
  });
  return response.data;
};

export const getAllQuizzes = async () => {
  const response = await axios.get(`${API_BASE_URL}/api/quizzes`);
  return response.data;
};

export const getQuizById = async (id) => {
  const response = await axios.get(`${API_BASE_URL}/api/quizzes/${id}`);
  return response.data;
};
