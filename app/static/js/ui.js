const UI = {
    // DOM元素引用
    elements: {
        projectList: document.getElementById('projectList'),
        projectSearch: document.getElementById('projectSearch'),
        newProjectBtn: document.getElementById('newProjectBtn'),
        settingsBtn: document.getElementById('settingsBtn'),
        documentHeader: document.getElementById('documentHeader'),
        documentContent: document.getElementById('documentContent'),
        chatMessages: document.getElementById('chatMessages'),
        questionInput: document.getElementById('questionInput'),
        sendBtn: document.getElementById('sendBtn'),
        modal: document.getElementById('modal'),
        modalTitle: document.getElementById('modalTitle'),
        modalContent: document.getElementById('modalContent'),
        modalConfirmBtn: document.getElementById('modalConfirmBtn'),
        modalCancelBtn: document.getElementById('modalCancelBtn'),
        loading: document.getElementById('loading')
    },

    // 当前状态
    state: {
        currentProjectId: null,
        currentDocBaseId: null,
        currentVersionId: null,
        currentSessionId: null,
        highlightedBlockId: null
    },

    // 初始化UI
    init() {
        this.bindEvents();
        this.loadProjects();
        this.checkApiKey();
    },

    // 绑定事件处理器
    bindEvents() {
        // 项目相关
        this.elements.newProjectBtn.addEventListener('click', () => this.showNewProjectModal());
        this.elements.projectSearch.addEventListener('input', (e) => this.filterProjects(e.target.value));
        
        // 设置相关
        this.elements.settingsBtn.addEventListener('click', () => this.showSettingsModal());
        
        // 问答相关
        this.elements.sendBtn.addEventListener('click', () => this.sendQuestion());
        this.elements.questionInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendQuestion();
            }
        });
        
        // 模态框
        this.elements.modalCancelBtn.addEventListener('click', () => this.hideModal());
    },

    // 显示加载动画
    showLoading() {
        this.elements.loading.classList.remove('hidden');
    },

    // 隐藏加载动画
    hideLoading() {
        this.elements.loading.classList.add('hidden');
    },

    // 显示模态框
    showModal(title, content, onConfirm) {
        this.elements.modalTitle.textContent = title;
        this.elements.modalContent.innerHTML = content;
        this.elements.modalConfirmBtn.onclick = onConfirm;
        this.elements.modal.classList.remove('hidden');
    },

    // 隐藏模态框
    hideModal() {
        this.elements.modal.classList.add('hidden');
    },

    // 显示新建项目模态框
    showNewProjectModal() {
        const content = `
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700">项目号</label>
                    <input type="text" id="newProjectId" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">项目名称（可选）</label>
                    <input type="text" id="newProjectName" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
                </div>
            </div>
        `;

        this.showModal('新建项目', content, async () => {
            const projectId = document.getElementById('newProjectId').value;
            const projectName = document.getElementById('newProjectName').value;
            
            if (!projectId) {
                alert('请输入项目号');
                return;
            }

            try {
                this.showLoading();
                await API.createProject(projectId, projectName);
                await this.loadProjects();
                this.hideModal();
            } catch (error) {
                alert('创建项目失败: ' + error.message);
            } finally {
                this.hideLoading();
            }
        });
    },

    // 显示设置模态框
    async showSettingsModal() {
        const { api_key } = await API.getApiKey();
        
        const content = `
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700">API Key</label>
                    <input type="text" id="apiKeyInput" value="${api_key || ''}" 
                           class="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
                </div>
            </div>
        `;

        this.showModal('设置', content, async () => {
            const apiKey = document.getElementById('apiKeyInput').value;
            
            try {
                this.showLoading();
                await API.updateApiKey(apiKey);
                this.hideModal();
            } catch (error) {
                alert('更新API Key失败: ' + error.message);
            } finally {
                this.hideLoading();
            }
        });
    },

    // 加载项目列表
    async loadProjects() {
        try {
            this.showLoading();
            const { projects } = await API.listProjects();
            
            this.elements.projectList.innerHTML = projects.map(project => `
                <div class="project-item mb-4 p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
                     data-project-id="${project.project_id}">
                    <div class="font-medium">${project.project_id}</div>
                    ${project.project_name ? `<div class="text-sm text-gray-500">${project.project_name}</div>` : ''}
                    <div class="documents-container mt-2 ml-4 hidden"></div>
                </div>
            `).join('');

            // 绑定项目点击事件
            this.elements.projectList.querySelectorAll('.project-item').forEach(item => {
                item.addEventListener('click', () => this.toggleProject(item));
            });
        } catch (error) {
            alert('加载项目列表失败: ' + error.message);
        } finally {
            this.hideLoading();
        }
    },

    // 切换项目展开/折叠
    async toggleProject(projectItem) {
        const projectId = projectItem.dataset.projectId;
        const documentsContainer = projectItem.querySelector('.documents-container');
        
        if (documentsContainer.classList.contains('hidden')) {
            try {
                this.showLoading();
                const { documents } = await API.listDocuments(projectId);
                
                documentsContainer.innerHTML = documents.map(doc => `
                    <div class="document-item mb-2 p-2 border rounded hover:bg-gray-100"
                         data-doc-base-id="${doc.doc_base_id}">
                        <div class="flex items-center justify-between">
                            <div>
                                <span class="font-medium">${doc.original_filename}</span>
                                ${doc.version_number ? `<span class="text-sm text-gray-500 ml-2">v${doc.version_number}</span>` : ''}
                            </div>
                            <button class="upload-version-btn text-primary text-sm">上传新版本</button>
                        </div>
                        <div class="versions-container mt-2 ml-4 hidden"></div>
                    </div>
                `).join('');

                // 绑定文档点击事件
                documentsContainer.querySelectorAll('.document-item').forEach(item => {
                    item.addEventListener('click', (e) => {
                        if (!e.target.classList.contains('upload-version-btn')) {
                            this.toggleDocument(item);
                        }
                    });
                });

                // 绑定上传新版本按钮事件
                documentsContainer.querySelectorAll('.upload-version-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const docBaseId = btn.closest('.document-item').dataset.docBaseId;
                        this.showUploadVersionModal(projectId, docBaseId);
                    });
                });

                documentsContainer.classList.remove('hidden');
            } catch (error) {
                alert('加载文档列表失败: ' + error.message);
            } finally {
                this.hideLoading();
            }
        } else {
            documentsContainer.classList.add('hidden');
        }
    },

    // 切换文档展开/折叠
    async toggleDocument(documentItem) {
        const docBaseId = documentItem.dataset.docBaseId;
        const versionsContainer = documentItem.querySelector('.versions-container');
        
        if (versionsContainer.classList.contains('hidden')) {
            try {
                this.showLoading();
                const { versions } = await API.listVersions(docBaseId);
                
                versionsContainer.innerHTML = versions.map(version => `
                    <div class="version-item p-2 flex items-center justify-between hover:bg-gray-50 cursor-pointer"
                         data-version-id="${version.version_id}">
                        <div>
                            <span>v${version.version_number}</span>
                            ${version.is_latest ? '<span class="text-primary ml-2">(最新)</span>' : ''}
                            <span class="text-sm text-gray-500 ml-2">${new Date(version.upload_time).toLocaleString()}</span>
                        </div>
                        ${!version.is_latest ? `
                            <button class="delete-version-btn text-red-500 text-sm">删除</button>
                        ` : ''}
                    </div>
                `).join('');

                // 绑定版本点击事件
                versionsContainer.querySelectorAll('.version-item').forEach(item => {
                    item.addEventListener('click', () => this.selectVersion(item));
                });

                // 绑定删除版本按钮事件
                versionsContainer.querySelectorAll('.delete-version-btn').forEach(btn => {
                    btn.addEventListener('click', async (e) => {
                        e.stopPropagation();
                        const versionId = btn.closest('.version-item').dataset.versionId;
                        if (confirm('确定要删除这个版本吗？')) {
                            try {
                                this.showLoading();
                                await API.softDeleteVersion(versionId);
                                await this.toggleDocument(documentItem);
                            } catch (error) {
                                alert('删除版本失败: ' + error.message);
                            } finally {
                                this.hideLoading();
                            }
                        }
                    });
                });

                versionsContainer.classList.remove('hidden');
            } catch (error) {
                alert('加载版本列表失败: ' + error.message);
            } finally {
                this.hideLoading();
            }
        } else {
            versionsContainer.classList.add('hidden');
        }
    },

    // 选择版本
    async selectVersion(versionItem) {
        const versionId = versionItem.dataset.versionId;
        this.state.currentVersionId = versionId;
        
        try {
            this.showLoading();
            
            // 创建新的聊天会话
            const { session_id } = await API.createChatSession(versionId);
            this.state.currentSessionId = session_id;
            
            // 清空聊天记录
            this.elements.chatMessages.innerHTML = '';
            
            // 加载聊天历史
            const { messages } = await API.getChatHistory(session_id);
            this.renderChatMessages(messages);
            
            // TODO: 加载文档预览
            
        } catch (error) {
            alert('加载版本失败: ' + error.message);
        } finally {
            this.hideLoading();
        }
    },

    // 显示上传新版本模态框
    showUploadVersionModal(projectId, docBaseId) {
        const content = `
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700">选择文件</label>
                    <input type="file" id="versionFileInput" accept=".docx" 
                           class="mt-1 block w-full">
                </div>
            </div>
        `;

        this.showModal('上传新版本', content, async () => {
            const fileInput = document.getElementById('versionFileInput');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('请选择文件');
                return;
            }

            try {
                this.showLoading();
                await API.uploadDocument(projectId, file);
                await this.loadProjects();
                this.hideModal();
            } catch (error) {
                alert('上传文件失败: ' + error.message);
            } finally {
                this.hideLoading();
            }
        });
    },

    // 发送问题
    async sendQuestion() {
        const query = this.elements.questionInput.value.trim();
        if (!query) return;
        
        if (!this.state.currentSessionId) {
            alert('请先选择一个文档版本');
            return;
        }

        try {
            this.showLoading();
            
            // 添加用户问题到聊天记录
            this.appendChatMessage({
                sender: 'user',
                text: query,
                timestamp: new Date().toISOString()
            });
            
            // 清空输入框
            this.elements.questionInput.value = '';
            
            // 发送问题并获取回答
            const response = await API.sendMessage(this.state.currentSessionId, query);
            
            // 添加系统回答到聊天记录
            this.appendChatMessage({
                sender: 'system',
                text: response.answer,
                retrieved_chunk_html_ids: JSON.stringify(response.sources),
                timestamp: new Date().toISOString()
            });
            
        } catch (error) {
            alert('发送问题失败: ' + error.message);
        } finally {
            this.hideLoading();
        }
    },

    // 渲染聊天消息
    renderChatMessages(messages) {
        this.elements.chatMessages.innerHTML = messages.map(msg => this.createMessageHTML(msg)).join('');
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
        
        // 绑定来源引用点击事件
        this.elements.chatMessages.querySelectorAll('.source-reference').forEach(ref => {
            ref.addEventListener('click', () => this.highlightSource(ref.dataset.htmlId));
        });
    },

    // 添加单条聊天消息
    appendChatMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.innerHTML = this.createMessageHTML(message);
        this.elements.chatMessages.appendChild(messageElement);
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
        
        // 绑定来源引用点击事件
        messageElement.querySelectorAll('.source-reference').forEach(ref => {
            ref.addEventListener('click', () => this.highlightSource(ref.dataset.htmlId));
        });
    },

    // 创建消息HTML
    createMessageHTML(message) {
        const isSystem = message.sender === 'system';
        const sources = message.retrieved_chunk_html_ids ? JSON.parse(message.retrieved_chunk_html_ids) : [];
        
        return `
            <div class="mb-4 ${isSystem ? 'pl-4' : 'pr-4'}">
                <div class="flex items-start ${isSystem ? 'flex-row' : 'flex-row-reverse'}">
                    <div class="flex-1 max-w-[80%]">
                        <div class="rounded-lg p-3 ${isSystem ? 'bg-gray-100' : 'bg-primary text-white'}">
                            ${message.text}
                        </div>
                        ${isSystem && sources.length > 0 ? `
                            <div class="mt-2 text-sm text-gray-500">
                                来源: ${sources.map((id, index) => `
                                    <a href="#" class="source-reference text-primary hover:underline" 
                                       data-html-id="${id}">[${index + 1}]</a>
                                `).join(' ')}
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    },

    // 高亮来源内容
    highlightSource(htmlId) {
        // 移除之前的高亮
        if (this.state.highlightedBlockId) {
            const prevBlock = document.getElementById(this.state.highlightedBlockId);
            if (prevBlock) {
                prevBlock.classList.remove('bg-yellow-100');
            }
        }
        
        // 添加新的高亮
        const block = document.getElementById(htmlId);
        if (block) {
            block.classList.add('bg-yellow-100');
            block.scrollIntoView({ behavior: 'smooth', block: 'center' });
            this.state.highlightedBlockId = htmlId;
        }
    },

    // 过滤项目列表
    filterProjects(searchText) {
        const projectItems = this.elements.projectList.querySelectorAll('.project-item');
        searchText = searchText.toLowerCase();
        
        projectItems.forEach(item => {
            const projectId = item.dataset.projectId.toLowerCase();
            const projectName = item.querySelector('.text-gray-500')?.textContent.toLowerCase() || '';
            
            if (projectId.includes(searchText) || projectName.includes(searchText)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    },

    // 检查API Key
    async checkApiKey() {
        try {
            const { api_key } = await API.getApiKey();
            if (!api_key) {
                this.showSettingsModal();
            }
        } catch (error) {
            console.error('检查API Key失败:', error);
        }
    }
}; 