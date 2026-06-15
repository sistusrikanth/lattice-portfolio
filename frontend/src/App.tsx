import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import IndexPage from "./pages/Index";
import WritingPage from "./pages/Writing";
import ArticlePage from "./pages/Article";
import SystemsPage from "./pages/Systems";
import PhotographyPage from "./pages/Photography";
import ProjectsPage from "./pages/Projects";
import AdminPage from "./pages/Admin";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<IndexPage />} />
        <Route path="writing" element={<WritingPage />} />
        <Route path="writing/:slug" element={<ArticlePage />} />
        <Route path="systems" element={<SystemsPage />} />
        <Route path="photography" element={<PhotographyPage />} />
        <Route path="projects" element={<ProjectsPage />} />
      </Route>
      <Route path="admin" element={<AdminPage />} />
    </Routes>
  );
}
