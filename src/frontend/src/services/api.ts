import axios, { AxiosError } from "axios";
import type {
  ApiResponse,
  CreateProjectRequest,
  ProjectDetail,
  ProjectListItem,
  RenderStatus,
} from "@/types/project";

const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: `${baseURL}/api/v1`,
  timeout: 30000,
});

apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = window.localStorage.getItem("authToken");
    const devUid = process.env.NEXT_PUBLIC_DEV_UID || "dev_user";
    config.headers.Authorization = `Bearer ${token ?? `dev:${devUid}`}`;
  }
  return config;
});

async function unwrap<T>(promise: Promise<{ data: ApiResponse<T> }>): Promise<T> {
  try {
    const res = await promise;
    if (res.data.success) return res.data.data;
    throw new Error(res.data.error.message);
  } catch (e) {
    const err = e as AxiosError<ApiResponse<T>>;
    const message =
      (err.response?.data as { error?: { message?: string } } | undefined)?.error?.message ??
      err.message ??
      "요청 처리 중 문제가 발생했습니다.";
    throw new Error(message);
  }
}

export const projectApi = {
  create: (body: CreateProjectRequest) =>
    unwrap<{ projectId: string; status: string }>(apiClient.post("/project/create", body)),

  get: (projectId: string) => unwrap<ProjectDetail>(apiClient.get(`/project/${projectId}`)),

  status: (projectId: string) => unwrap<RenderStatus>(apiClient.get(`/render/status/${projectId}`)),

  restart: (projectId: string, fromStep: string) =>
    unwrap<{ projectId: string; status: string }>(
      apiClient.post("/project/restart", { projectId, fromStep })
    ),

  list: () => unwrap<{ items: ProjectListItem[] }>(apiClient.get("/projects")),

  cancel: (projectId: string) =>
    unwrap<{ projectId: string; status: string }>(
      apiClient.post("/project/cancel", { projectId })
    ),
};
