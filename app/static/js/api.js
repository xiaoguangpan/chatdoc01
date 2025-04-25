const API = {
    baseUrl: 'http://127.0.0.1:8000/api',

    // 项目相关
    async createProject(projectId, projectName) {
        const response = await fetch(`${this.baseUrl}/projects/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ project_id: projectId, project_name: projectName })
        });
        return await response.json();
    },

    async listProjects() {
        const response = await fetch(`${this.baseUrl}/projects/`);
        return await response.json();
    },

    // 文档相关
    async uploadDocument(projectId, file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('project_id', projectId);

        const response = await fetch(`${this.baseUrl}/documents/upload/`, {
            method: 'POST',
            body: formData
        });
        return await response.json();
    },

    async listDocuments(projectId) {
        const response = await fetch(`${this.baseUrl}/documents/${projectId}`);
        return await response.json();
    },

    async listVersions(docBaseId) {
        const response = await fetch(`${this.baseUrl}/documents/${docBaseId}/versions`);
        return await response.json();
    },

    async softDeleteVersion(versionId) {
        const response = await fetch(`${this.baseUrl}/versions/${versionId}`, {
            method: 'DELETE'
        });
        return await response.json();
    },

    // 聊天相关
    async createChatSession(versionId) {
        const response = await fetch(`${this.baseUrl}/chat/sessions/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ version_id: versionId })
        });
        return await response.json();
    },

    async sendMessage(sessionId, query) {
        const response = await fetch(`${this.baseUrl}/chat/${sessionId}/messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        return await response.json();
    },

    async getChatHistory(sessionId) {
        const response = await fetch(`${this.baseUrl}/chat/${sessionId}/messages`);
        return await response.json();
    },

    // 设置相关
    async updateApiKey(apiKey) {
        const response = await fetch(`${this.baseUrl}/settings/api-key`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ api_key: apiKey })
        });
        return await response.json();
    },

    async getApiKey() {
        const response = await fetch(`${this.baseUrl}/settings/api-key`);
        return await response.json();
    }
}; 