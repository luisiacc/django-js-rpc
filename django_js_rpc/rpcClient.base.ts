import {
  QueryClient,
  QueryClientProvider,
  useQuery,
  useMutation,
} from "react-query";

interface FetchMethod {
  (url: string, options?: RequestInit): Promise<any>;
}

class RpcClient {
  private baseUrl: string;
  private fetchMethod: FetchMethod;

  constructor(fetchMethod: FetchMethod, baseUrl: string = "/api") {
    this.fetchMethod = fetchMethod;
    this.baseUrl = baseUrl;
  }

  private async request(method: string, path: string, data?: any) {
    const url = `${this.baseUrl}${path}`;
    const options: RequestInit = {
      method,
      headers: {
        "Content-Type": "application/json",
      },
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    const response = await this.fetchMethod(url, options);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  }

  private reverse(pattern: string, params: Record<string, string>): string {
    let url = pattern;
    for (const [key, value] of Object.entries(params)) {
      url = url.replace(`\${${key}}`, value);
    }
    return url;
  }

  // DYNAMIC_CONTENT_PLACEHOLDER
}

export default RpcClient;
