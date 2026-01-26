<template>
  <div class="settings-container">
    <h2 style="margin-bottom: 20px;">⚙️ 系统设置</h2>
    
    <div class="settings-layout">
      <!-- 侧边栏 -->
      <div class="settings-sidebar">
        <el-menu :default-active="activeTab" @select="handleTabChange">
          <el-menu-item index="tutorial">
            <el-icon><Reading /></el-icon>
            <span>服务器连接教程</span>
          </el-menu-item>
          <el-menu-item index="config">
            <el-icon><Setting /></el-icon>
            <span>TensorBoard 配置</span>
          </el-menu-item>
          <el-menu-item index="presets">
            <el-icon><Collection /></el-icon>
            <span>常用配置</span>
          </el-menu-item>
          <el-menu-item index="notebook">
            <el-icon><Document /></el-icon>
            <span>模块配置</span>
          </el-menu-item>
        </el-menu>
      </div>
      
      <!-- 主内容区 -->
      <div class="settings-content">
        <!-- 服务器连接教程 -->
        <div v-if="activeTab === 'tutorial'" class="tutorial-section">
          <el-card>
            <template #header>
              <div class="card-header">
                <span class="card-title">📚 服务器连接教程</span>
              </div>
            </template>
            
            <!-- 参数配置区 -->
            <div class="params-config">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <el-alert
                  title="填写你的服务器信息，下方命令会自动更新"
                  type="info"
                  :closable="false"
                  style="flex: 1; margin-right: 12px;"
                />
                <div style="display: flex; gap: 8px;">
                  <el-button v-if="!isEditingParams" size="small" @click="enableParamsEdit">
                    <el-icon><Edit /></el-icon>
                    编辑
                  </el-button>
                  <template v-else>
                    <el-button size="small" @click="cancelParamsEdit">
                      <el-icon><Close /></el-icon>
                      取消
                    </el-button>
                    <el-button type="primary" size="small" @click="saveParams">
                      <el-icon><Check /></el-icon>
                      保存
                    </el-button>
                  </template>
                </div>
              </div>
              <el-form label-width="120px" size="small">
                <div class="param-section">
                  <div class="param-section-title">服务器参数</div>
                  <el-row :gutter="16">
                    <el-col :span="12">
                      <el-form-item label="服务器别名">
                        <el-input v-model="tutorialParams.serverAlias" :disabled="!isEditingParams" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="服务器 IP">
                        <el-input v-model="tutorialParams.serverIp" :disabled="!isEditingParams" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="16">
                    <el-col :span="12">
                      <el-form-item label="服务器用户名">
                        <el-input v-model="tutorialParams.username" :disabled="!isEditingParams" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="SSH 端口">
                        <el-input v-model="tutorialParams.port" :disabled="!isEditingParams" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
                
                <div class="param-section">
                  <div class="param-section-title">
                    跳板机参数
                    <el-tag size="small" type="info" style="margin-left: 8px;">可选</el-tag>
                  </div>
                  <el-row :gutter="16">
                    <el-col :span="12">
                      <el-form-item label="跳板机用户名">
                        <el-input v-model="tutorialParams.jumpUser" :disabled="!isEditingParams" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="跳板机 IP">
                        <el-input v-model="tutorialParams.jumpHost" :disabled="!isEditingParams" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
              </el-form>
            </div>
            
            <!-- SSH Config 配置教程 -->
            <div class="tutorial-block">
              <h3>
                <el-icon><Document /></el-icon>
                一、配置 SSH Config 文件
              </h3>
              <p class="tutorial-desc">
                SSH Config 文件可以简化 SSH 连接命令，支持跳板机、代理等复杂网络环境。
              </p>
              
              <el-tabs v-model="configOs" type="border-card">
                <el-tab-pane label="Linux" name="linux">
                  <div class="tutorial-content">
                    <h4>1. 打开或创建 SSH Config 文件</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">nano ~/.ssh/config</pre>
                      <el-button size="small" @click="copyToClipboard('nano ~/.ssh/config')" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">如果文件不存在，会自动创建。也可以使用 vim 或其他编辑器。</p>
                    
                    <h4>2. 添加主机配置</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">Host {{ tutorialParams.serverAlias }}
  HostName {{ tutorialParams.serverIp }}
  User {{ tutorialParams.username }}
  Port {{ tutorialParams.port }}
  IdentityFile ~/.ssh/id_rsa</pre>
                      <el-button size="small" @click="copyToClipboard(`Host ${tutorialParams.serverAlias}\n  HostName ${tutorialParams.serverIp}\n  User ${tutorialParams.username}\n  Port ${tutorialParams.port}\n  IdentityFile ~/.ssh/id_rsa`)" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">
                      <strong>参数说明：</strong><br>
                      • <code>Host</code>: 主机别名，可以自定义（如 LabServer）<br>
                      • <code>HostName</code>: 服务器 IP 地址或域名<br>
                      • <code>User</code>: SSH 登录用户名<br>
                      • <code>Port</code>: SSH 端口（默认 22）<br>
                      • <code>IdentityFile</code>: 私钥文件路径（可选）
                    </p>
                    
                    <h4>3. 使用跳板机（可选）</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">Host {{ tutorialParams.serverAlias }}
  HostName {{ tutorialParams.serverIp }}
  User {{ tutorialParams.username }}
  Port {{ tutorialParams.port }}
  ProxyJump {{ tutorialParams.jumpUser }}@{{ tutorialParams.jumpHost }}</pre>
                      <el-button size="small" @click="copyToClipboard(`Host ${tutorialParams.serverAlias}\n  HostName ${tutorialParams.serverIp}\n  User ${tutorialParams.username}\n  Port ${tutorialParams.port}\n  ProxyJump {{ tutorialParams.jumpUser }}@{{ tutorialParams.jumpHost }}`)" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">如果需要通过跳板机连接，添加 <code>ProxyJump</code> 参数。</p>
                    
                    <h4>4. 保存并设置权限</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">chmod 600 ~/.ssh/config</pre>
                      <el-button size="small" @click="copyToClipboard('chmod 600 ~/.ssh/config')" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">确保配置文件权限正确，否则 SSH 会拒绝使用。</p>
                    
                    <h4>5. 测试连接</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">ssh {{ tutorialParams.serverAlias }}</pre>
                      <el-button size="small" @click="copyToClipboard(`ssh ${tutorialParams.serverAlias}`)" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">现在可以直接使用别名连接服务器了！</p>
                  </div>
                </el-tab-pane>
                
                <el-tab-pane label="macOS" name="macos">
                  <div class="tutorial-content">
                    <h4>1. 打开或创建 SSH Config 文件</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">nano ~/.ssh/config</pre>
                      <el-button size="small" @click="copyToClipboard('nano ~/.ssh/config')" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">如果文件不存在，会自动创建。也可以使用 vim 或其他编辑器。</p>
                    
                    <h4>2. 添加主机配置</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">Host {{ tutorialParams.serverAlias }}
  HostName {{ tutorialParams.serverIp }}
  User {{ tutorialParams.username }}
  Port {{ tutorialParams.port }}
  IdentityFile ~/.ssh/id_rsa
  UseKeychain yes
  AddKeysToAgent yes</pre>
                      <el-button size="small" @click="copyToClipboard(`Host ${tutorialParams.serverAlias}\n  HostName ${tutorialParams.serverIp}\n  User ${tutorialParams.username}\n  Port ${tutorialParams.port}\n  IdentityFile ~/.ssh/id_rsa\n  UseKeychain yes\n  AddKeysToAgent yes`)" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">
                      <strong>参数说明：</strong><br>
                      • <code>Host</code>: 主机别名，可以自定义（如 LabServer）<br>
                      • <code>HostName</code>: 服务器 IP 地址或域名<br>
                      • <code>User</code>: SSH 登录用户名<br>
                      • <code>Port</code>: SSH 端口（默认 22）<br>
                      • <code>IdentityFile</code>: 私钥文件路径（可选）<br>
                      • <code>UseKeychain</code>: 将密钥保存到 macOS 钥匙串（推荐）<br>
                      • <code>AddKeysToAgent</code>: 自动添加密钥到 ssh-agent
                    </p>
                    
                    <h4>3. 使用跳板机（可选）</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">Host {{ tutorialParams.serverAlias }}
  HostName {{ tutorialParams.serverIp }}
  User {{ tutorialParams.username }}
  Port {{ tutorialParams.port }}
  ProxyJump {{ tutorialParams.jumpUser }}@{{ tutorialParams.jumpHost }}</pre>
                      <el-button size="small" @click="copyToClipboard(`Host ${tutorialParams.serverAlias}\n  HostName ${tutorialParams.serverIp}\n  User ${tutorialParams.username}\n  Port ${tutorialParams.port}\n  ProxyJump {{ tutorialParams.jumpUser }}@{{ tutorialParams.jumpHost }}`)" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">如果需要通过跳板机连接，添加 <code>ProxyJump</code> 参数。</p>
                    
                    <h4>4. 保存并设置权限</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">chmod 600 ~/.ssh/config</pre>
                      <el-button size="small" @click="copyToClipboard('chmod 600 ~/.ssh/config')" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">确保配置文件权限正确，否则 SSH 会拒绝使用。</p>
                    
                    <h4>5. 测试连接</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">ssh {{ tutorialParams.serverAlias }}</pre>
                      <el-button size="small" @click="copyToClipboard(`ssh ${tutorialParams.serverAlias}`)" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">现在可以直接使用别名连接服务器了！</p>
                  </div>
                </el-tab-pane>
                
                <el-tab-pane label="Windows" name="windows">
                  <div class="tutorial-content">
                    <h4>1. 打开或创建 SSH Config 文件</h4>
                    <p class="tip">Windows 10/11 自带 OpenSSH 客户端，配置文件位置：</p>
                    <div class="code-block-wrapper">
                      <pre class="code-block">C:\Users\你的用户名\.ssh\config</pre>
                      <el-button size="small" @click="copyToClipboard('C:\\Users\\你的用户名\\.ssh\\config')" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">使用记事本或 VS Code 打开（如果不存在则创建）：</p>
                    <div class="code-block-wrapper">
                      <pre class="code-block">notepad %USERPROFILE%\.ssh\config</pre>
                      <el-button size="small" @click="copyToClipboard('notepad %USERPROFILE%\\.ssh\\config')" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    
                    <h4>2. 添加主机配置</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">Host {{ tutorialParams.serverAlias }}
  HostName {{ tutorialParams.serverIp }}
  User {{ tutorialParams.username }}
  Port {{ tutorialParams.port }}
  IdentityFile C:\Users\你的用户名\.ssh\id_rsa</pre>
                      <el-button size="small" @click="copyToClipboard(`Host ${tutorialParams.serverAlias}\n  HostName ${tutorialParams.serverIp}\n  User ${tutorialParams.username}\n  Port ${tutorialParams.port}\n  IdentityFile C:\\\\Users\\\\你的用户名\\\\.ssh\\\\id_rsa`)" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">
                      <strong>参数说明：</strong><br>
                      • <code>Host</code>: 主机别名，可以自定义（如 LabServer）<br>
                      • <code>HostName</code>: 服务器 IP 地址或域名<br>
                      • <code>User</code>: SSH 登录用户名<br>
                      • <code>Port</code>: SSH 端口（默认 22）<br>
                      • <code>IdentityFile</code>: 私钥文件路径（使用反斜杠或正斜杠）
                    </p>
                    
                    <h4>3. 使用跳板机（可选）</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">Host {{ tutorialParams.serverAlias }}
  HostName {{ tutorialParams.serverIp }}
  User {{ tutorialParams.username }}
  Port {{ tutorialParams.port }}
  ProxyJump {{ tutorialParams.jumpUser }}@{{ tutorialParams.jumpHost }}</pre>
                      <el-button size="small" @click="copyToClipboard(`Host ${tutorialParams.serverAlias}\n  HostName ${tutorialParams.serverIp}\n  User ${tutorialParams.username}\n  Port ${tutorialParams.port}\n  ProxyJump {{ tutorialParams.jumpUser }}@{{ tutorialParams.jumpHost }}`)" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">如果需要通过跳板机连接，添加 <code>ProxyJump</code> 参数。</p>
                    
                    <h4>4. 测试连接</h4>
                    <p class="tip">打开 PowerShell 或 CMD，运行：</p>
                    <div class="code-block-wrapper">
                      <pre class="code-block">ssh {{ tutorialParams.serverAlias }}</pre>
                      <el-button size="small" @click="copyToClipboard(`ssh ${tutorialParams.serverAlias}`)" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">现在可以直接使用别名连接服务器了！</p>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </div>
            
            <!-- SSH 免密登录教程 -->
            <div class="tutorial-block">
              <h3>
                <el-icon><Key /></el-icon>
                二、配置 SSH 免密登录
              </h3>
              <p class="tutorial-desc">
                配置免密登录后，无需每次输入密码即可连接服务器，提升使用体验。
              </p>
              
              <el-tabs v-model="keygenOs" type="border-card">
                <el-tab-pane label="Linux" name="linux">
                  <div class="tutorial-content">
                    <h4>步骤 1：生成 SSH 密钥对</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">ssh-keygen -t rsa -b 4096</pre>
                      <el-button size="small" @click="copySshKeygen" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">
                      按提示操作：<br>
                      • 询问保存位置时，直接回车使用默认路径 <code>~/.ssh/id_rsa</code><br>
                      • 询问密码时，可以直接回车（不设置密码）或输入密码（更安全）
                    </p>
                    
                    <h4>步骤 2：复制公钥到服务器</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">ssh-copy-id {{ tutorialParams.username }}@{{ tutorialParams.serverIp }}</pre>
                      <el-button size="small" @click="copyToClipboard('ssh-copy-id ' + tutorialParams.username + '@' + tutorialParams.serverIp)" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">
                      如果使用了 SSH Config 别名：
                    </p>
                    <div class="code-block-wrapper">
                      <pre class="code-block">ssh-copy-id {{ tutorialParams.serverAlias }}</pre>
                      <el-button size="small" @click="copyToClipboard('ssh-copy-id ' + tutorialParams.serverAlias)" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">输入一次服务器密码后，公钥会自动添加到服务器的 <code>~/.ssh/authorized_keys</code> 文件。</p>
                    
                    <h4>步骤 3：测试免密登录</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">ssh {{ tutorialParams.serverAlias }}</pre>
                      <el-button size="small" @click="copyToClipboard('ssh ' + tutorialParams.serverAlias)" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">如果配置成功，应该无需输入密码即可登录！</p>
                    
                    <div class="warning-box">
                      <strong>⚠️ 故障排查：</strong><br>
                      如果仍需要密码，检查服务器端权限：<br>
                      <code>chmod 700 ~/.ssh</code><br>
                      <code>chmod 600 ~/.ssh/authorized_keys</code>
                    </div>
                  </div>
                </el-tab-pane>
                
                <el-tab-pane label="macOS" name="macos">
                  <div class="tutorial-content">
                    <h4>步骤 1：生成 SSH 密钥对</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">ssh-keygen -t rsa -b 4096</pre>
                      <el-button size="small" @click="copySshKeygen" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">
                      按提示操作：<br>
                      • 询问保存位置时，直接回车使用默认路径 <code>~/.ssh/id_rsa</code><br>
                      • 询问密码时，可以直接回车（不设置密码）或输入密码（更安全）
                    </p>
                    
                    <h4>步骤 2：复制公钥到服务器</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">ssh-copy-id {{ tutorialParams.username }}@{{ tutorialParams.serverIp }}</pre>
                      <el-button size="small" @click="copyToClipboard('ssh-copy-id ' + tutorialParams.username + '@' + tutorialParams.serverIp)" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">
                      如果使用了 SSH Config 别名：
                    </p>
                    <div class="code-block-wrapper">
                      <pre class="code-block">ssh-copy-id {{ tutorialParams.serverAlias }}</pre>
                      <el-button size="small" @click="copyToClipboard('ssh-copy-id ' + tutorialParams.serverAlias)" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">输入一次服务器密码后，公钥会自动添加到服务器的 <code>~/.ssh/authorized_keys</code> 文件。</p>
                    
                    <h4>步骤 3：测试免密登录</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">ssh {{ tutorialParams.serverAlias }}</pre>
                      <el-button size="small" @click="copyToClipboard('ssh ' + tutorialParams.serverAlias)" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">如果配置成功，应该无需输入密码即可登录！</p>
                    
                    <h4>额外步骤：添加密钥到 macOS 钥匙串（可选）</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">ssh-add --apple-use-keychain ~/.ssh/id_rsa</pre>
                      <el-button size="small" @click="copyToClipboard('ssh-add --apple-use-keychain ~/.ssh/id_rsa')" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">这样密钥会保存到 macOS 钥匙串，重启后无需重新添加。</p>
                    
                    <div class="warning-box">
                      <strong>⚠️ 故障排查：</strong><br>
                      如果仍需要密码，检查服务器端权限：<br>
                      <code>chmod 700 ~/.ssh</code><br>
                      <code>chmod 600 ~/.ssh/authorized_keys</code>
                    </div>
                  </div>
                </el-tab-pane>
                
                <el-tab-pane label="Windows" name="windows">
                  <div class="tutorial-content">
                    <h4>步骤 1：生成 SSH 密钥对</h4>
                    <p class="tip">打开 PowerShell，运行：</p>
                    <div class="code-block-wrapper">
                      <pre class="code-block">ssh-keygen -t rsa -b 4096</pre>
                      <el-button size="small" @click="copySshKeygen" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">
                      按提示操作：<br>
                      • 询问保存位置时，直接回车使用默认路径 <code>C:\Users\你的用户名\.ssh\id_rsa</code><br>
                      • 询问密码时，可以直接回车（不设置密码）或输入密码（更安全）
                    </p>
                    
                    <h4>步骤 2：复制公钥到服务器</h4>
                    <p class="tip">Windows 可能没有 <code>ssh-copy-id</code> 命令，需要手动复制：</p>
                    
                    <p class="tip"><strong>方法 1：使用 PowerShell 命令</strong></p>
                    <div class="code-block-wrapper">
                      <pre class="code-block">type $env:USERPROFILE\.ssh\id_rsa.pub | ssh {{ tutorialParams.username }}@{{ tutorialParams.serverIp }} "cat >> ~/.ssh/authorized_keys"</pre>
                      <el-button size="small" @click="copyWindowsSshCopyId" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    
                    <p class="tip"><strong>方法 2：手动复制</strong></p>
                    <p class="tip">① 查看公钥内容：</p>
                    <div class="code-block-wrapper">
                      <pre class="code-block">type %USERPROFILE%\.ssh\id_rsa.pub</pre>
                      <el-button size="small" @click="copyToClipboard('type %USERPROFILE%\\.ssh\\id_rsa.pub')" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">② 复制输出的内容</p>
                    <p class="tip">③ SSH 登录到服务器：</p>
                    <div class="code-block-wrapper">
                      <pre class="code-block">ssh {{ tutorialParams.username }}@{{ tutorialParams.serverIp }}</pre>
                      <el-button size="small" @click="copyToClipboard('ssh ' + tutorialParams.username + '@' + tutorialParams.serverIp)" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">④ 在服务器上执行：</p>
                    <div class="code-block-wrapper">
                      <pre class="code-block">mkdir -p ~/.ssh
echo "粘贴你的公钥内容" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys</pre>
                      <el-button size="small" @click="copyServerSetup" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    
                    <h4>步骤 3：测试免密登录</h4>
                    <div class="code-block-wrapper">
                      <pre class="code-block">ssh {{ tutorialParams.serverAlias }}</pre>
                      <el-button size="small" @click="copyToClipboard('ssh ' + tutorialParams.serverAlias)" class="copy-btn">
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <p class="tip">如果配置成功，应该无需输入密码即可登录！</p>
                    
                    <div class="warning-box">
                      <strong>⚠️ 故障排查：</strong><br>
                      • 确保 Windows 已安装 OpenSSH 客户端（Windows 10/11 自带）<br>
                      • 检查服务器端 <code>~/.ssh/authorized_keys</code> 文件权限<br>
                      • 如果使用 Git Bash，命令与 Linux 相同
                    </div>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </div>
          </el-card>
        </div>
        
        <!-- TensorBoard 配置 -->
        <div v-if="activeTab === 'config'">
          <el-card>
            <template #header>
              <div class="card-header">
                <span class="card-title">⚙️ TensorBoard 配置</span>
              </div>
            </template>
            
            <el-form :model="config" label-width="200px">
              <el-form-item label="运行模式">
                <el-radio-group v-model="config.mode" :disabled="!isEditing" style="display: flex; flex-direction: column; gap: 12px; align-items: flex-start;">
                  <el-radio label="local">
                    <span style="font-weight: 500;">本地模式</span>
                    <span style="font-size: 13px; color: #909399; margin-left: 8px;">
                      - TensorBoard 日志文件在本机
                    </span>
                  </el-radio>
                  <el-radio label="remote">
                    <span style="font-weight: 500;">远程模式</span>
                    <span style="font-size: 13px; color: #909399; margin-left: 8px;">
                      - 通过 SSH 连接远程服务器（支持直接 IP 或 SSH Config 别名）
                    </span>
                  </el-radio>
                </el-radio-group>
              </el-form-item>
              
              <template v-if="config.mode === 'remote'">
                <el-form-item label="连接方式">
                  <el-radio-group v-model="connectionType" :disabled="!isEditing">
                    <el-radio label="direct">直接连接（IP + 端口）</el-radio>
                    <el-radio label="ssh_config">SSH Config 别名</el-radio>
                  </el-radio-group>
                </el-form-item>
                
                <template v-if="connectionType === 'direct'">
                  <el-form-item label="服务器地址">
                    <el-input v-model="directConfig.host" :disabled="!isEditing" placeholder="例如: 192.168.1.100" />
                  </el-form-item>
                  
                  <el-form-item label="用户名">
                    <el-input v-model="directConfig.user" :disabled="!isEditing" placeholder="SSH 用户名" />
                  </el-form-item>
                  
                  <el-form-item label="SSH 端口">
                    <el-input-number v-model="directConfig.port" :disabled="!isEditing" :min="1" :max="65535" />
                  </el-form-item>
                </template>
                
                <template v-if="connectionType === 'ssh_config'">
                  <el-form-item label="主机别名">
                    <el-input v-model="sshConfigConfig.host" :disabled="!isEditing" placeholder="例如: LabServer" />
                    <div style="font-size: 12px; color: #909399; margin-top: 8px;">
                      填写在 ~/.ssh/config 中定义的 Host 名称。<br>
                      配置方法请查看左侧"服务器连接教程"。
                    </div>
                  </el-form-item>
                </template>
                
                <el-form-item label="TensorBoard 输出路径">
                  <el-input 
                    v-if="connectionType === 'direct'"
                    v-model="directConfig.tensorboard_base_path" 
                    :disabled="!isEditing"
                    placeholder="例如: /home/user/pymarl/results/tb_logs 或留空"
                  />
                  <el-input 
                    v-else
                    v-model="sshConfigConfig.tensorboard_base_path" 
                    :disabled="!isEditing"
                    placeholder="例如: /home/user/pymarl/results/tb_logs 或留空"
                  />
                  <div style="font-size: 12px; color: #909399; margin-top: 8px;">
                    <strong>可选配置</strong>：远程服务器上 TensorBoard 日志的基础目录。<br>
                    留空则在创建实验时填写完整的绝对路径。<br>
                    填写后可以在创建实验时使用相对路径（相对于此基础路径）。
                  </div>
                </el-form-item>
                
                <el-form-item label="TensorBoard 命令">
                  <el-input 
                    v-if="connectionType === 'direct'"
                    v-model="directConfig.tensorboard_cmd" 
                    :disabled="!isEditing"
                    placeholder="例如: /home/user/.conda/envs/myenv/bin/tensorboard"
                  />
                  <el-input 
                    v-else
                    v-model="sshConfigConfig.tensorboard_cmd" 
                    :disabled="!isEditing"
                    placeholder="例如: /home/user/.conda/envs/myenv/bin/tensorboard"
                  />
                  <div style="font-size: 12px; color: #909399; margin-top: 8px;">
                    <strong>必填配置</strong>：TensorBoard 可执行文件的完整路径。<br>
                    <strong>如何查找：</strong>SSH 登录到服务器后，运行 <code>which tensorboard</code><br>
                    例如：<code>/home/user/.conda/envs/myenv/bin/tensorboard</code>
                  </div>
                </el-form-item>
                
                <el-form-item label="TensorBoard 路径参数名">
                  <el-input 
                    v-if="connectionType === 'direct'"
                    v-model="directConfig.tensorboard_param_name" 
                    :disabled="!isEditing"
                    placeholder="例如: local_results_path"
                  />
                  <el-input 
                    v-else
                    v-model="sshConfigConfig.tensorboard_param_name" 
                    :disabled="!isEditing"
                    placeholder="例如: local_results_path"
                  />
                  <div style="font-size: 12px; color: #909399; margin-top: 8px;">
                    <strong>可选配置</strong>：用于指定 TensorBoard 日志路径的参数名称。<br>
                    <strong>PyMARL 框架：</strong><code>local_results_path</code><br>
                    <strong>其他框架：</strong>根据你的框架文档填写，如 <code>logdir</code>、<code>log_path</code> 等<br>
                    留空则不在命令中添加 TensorBoard 路径参数（需要手动在配置参数中添加）
                  </div>
                </el-form-item>
                
                <el-form-item label="测试连接">
                  <el-input 
                    :value="testCommand" 
                    readonly
                    style="font-family: monospace;"
                  >
                    <template #append>
                      <el-button @click="copyCommand">
                        <el-icon><CopyDocument /></el-icon>
                        复制
                      </el-button>
                    </template>
                  </el-input>
                  <div style="font-size: 12px; color: #909399; margin-top: 8px;">
                    在终端运行此命令测试 SSH 连接是否正常
                  </div>
                </el-form-item>
                
                <div style="background: #f5f7fa; padding: 12px; border-radius: 4px; font-size: 13px; color: #606266; line-height: 1.6; margin-bottom: 20px;">
                  <strong>提示：</strong>需要配置 SSH 免密登录才能正常使用。<br>
                  如果使用跳板机或 Tailscale 等复杂网络环境，推荐使用 SSH Config 别名方式。
                </div>
                
                <!-- 本地 TensorBoard 配置 -->
                <el-divider content-position="center">
                  <span style="font-size: 14px; color: #606266;">⚡ 本地 TensorBoard 加速（推荐）</span>
                </el-divider>
                
                <el-form-item label="启用本地 TensorBoard">
                  <div>
                    <el-switch 
                      v-model="localTensorboardConfig.enabled" 
                      :disabled="!isEditing"
                      active-text="启用"
                      inactive-text="禁用"
                    />
                    <div style="font-size: 12px; color: #909399; margin-top: 8px;">
                      <strong>推荐启用</strong>：导入实验时自动下载 event 文件到本地，后续启动 TensorBoard 时直接使用本地文件，<br>
                      <strong>加速效果</strong>：启动时间从 ~20秒 缩短到 ~1秒，且更稳定。
                    </div>
                  </div>
                </el-form-item>
                
                <el-form-item v-if="localTensorboardConfig.enabled" label="本地 TensorBoard 命令">
                  <el-input 
                    v-model="localTensorboardConfig.command" 
                    :disabled="!isEditing"
                    placeholder="例如: tensorboard 或 /path/to/venv/bin/tensorboard"
                  />
                  <div style="font-size: 12px; color: #909399; margin-top: 8px;">
                    本地机器上的 TensorBoard 命令路径。<br>
                    如果已安装在系统环境中，直接填写 <code>tensorboard</code> 即可。<br>
                    如果在虚拟环境中，填写完整路径，如 <code>/Users/xxx/venv/bin/tensorboard</code>
                  </div>
                </el-form-item>
              </template>
              
              <div style="margin-top: 20px;">
                <el-button 
                  v-if="isEditing" 
                  type="primary" 
                  @click="saveConfig" 
                  :loading="saving"
                  style="width: 100%;"
                >
                  保存配置
                </el-button>
                <el-button 
                  v-else 
                  type="warning" 
                  @click="enableEdit"
                  style="width: 100%;"
                >
                  编辑配置
                </el-button>
              </div>
            </el-form>
          </el-card>
        </div>
        
        <!-- 常用配置 -->
        <div v-if="activeTab === 'presets'">
          <el-card>
            <template #header>
              <div class="card-header">
                <span class="card-title">🎯 常用配置</span>
                <div style="display: flex; gap: 8px;">
                  <el-button v-if="!isEditingPresets" size="small" @click="enablePresetsEdit">
                    <el-icon><Edit /></el-icon>
                    编辑
                  </el-button>
                  <template v-else>
                    <el-button size="small" @click="cancelPresetsEdit">
                      <el-icon><Close /></el-icon>
                      取消
                    </el-button>
                    <el-button type="primary" size="small" @click="savePresetsConfig">
                      <el-icon><Check /></el-icon>
                      保存
                    </el-button>
                  </template>
                </div>
              </div>
            </template>
            
            <el-alert
              title="配置常用的算法名和环境名，创建实验时可以快速选择"
              type="info"
              :closable="false"
              style="margin-bottom: 20px;"
            />
            
            <!-- 算法配置 -->
            <div class="preset-section">
              <div class="preset-section-title">
                <el-icon><Cpu /></el-icon>
                <span>算法列表</span>
                <el-button v-if="isEditingPresets" size="small" @click="addAlgorithm">
                  <el-icon><CirclePlus /></el-icon>
                  添加算法
                </el-button>
              </div>
              
              <!-- 编辑模式 -->
              <div v-if="isEditingPresets" class="algo-edit-list">
                <div v-for="(algo, index) in presets.algorithms" :key="index" class="algo-edit-item">
                  <el-input 
                    v-model="presets.algorithms[index]" 
                    placeholder="如: QMIX"
                    size="default"
                  />
                  <el-button 
                    size="small" 
                    type="danger" 
                    text
                    @click="removeAlgorithm(index)"
                  >
                    <el-icon><Close /></el-icon>
                  </el-button>
                </div>
                <div v-if="presets.algorithms.length === 0" class="preset-empty">
                  暂无算法，点击"添加算法"开始配置
                </div>
              </div>
              
              <!-- 查看模式 -->
              <div v-else class="algo-view-list">
                <div v-for="(algo, index) in presets.algorithms" :key="index" class="algo-view-item">
                  {{ algo }}
                </div>
                <div v-if="presets.algorithms.length === 0" class="preset-empty">
                  暂无算法配置
                </div>
              </div>
            </div>
            
            <!-- 环境配置 -->
            <div class="preset-section">
              <div class="preset-section-title">
                <el-icon><MapLocation /></el-icon>
                <span>环境与地图配置</span>
                <el-button v-if="isEditingPresets" size="small" @click="addEnvironment">
                  <el-icon><CirclePlus /></el-icon>
                  添加环境
                </el-button>
              </div>
              
              <!-- 编辑模式 -->
              <div v-if="isEditingPresets" class="env-edit-list">
                <div v-for="(env, index) in presets.environments" :key="index" class="env-edit-item">
                  <div class="env-item-header" @click="toggleEnvExpand(index)">
                    <div class="env-item-left">
                      <el-icon class="expand-icon" :class="{ expanded: env.expanded }">
                        <ArrowRight />
                      </el-icon>
                      <el-input 
                        v-model="env.name" 
                        placeholder="环境名，如: sc2"
                        size="default"
                        class="env-name-input-inline"
                        @click.stop
                      />
                      <span class="env-map-count">{{ env.maps.length }} 个地图</span>
                    </div>
                    <el-button 
                      size="small" 
                      type="danger"
                      @click.stop="confirmRemoveEnvironment(index)"
                    >
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
                  </div>
                  
                  <div v-show="env.expanded" class="env-maps-content">
                    <div class="env-maps-toolbar">
                      <span class="maps-label">地图列表</span>
                      <el-button size="small" type="primary" text @click="addMap(index)">
                        <el-icon><CirclePlus /></el-icon>
                        添加地图
                      </el-button>
                    </div>
                    <div class="env-maps-grid">
                      <div v-for="(map, mapIndex) in env.maps" :key="mapIndex" class="map-edit-item">
                        <el-input 
                          v-model="env.maps[mapIndex]" 
                          placeholder="如: 3m"
                          size="small"
                        />
                        <el-button 
                          size="small" 
                          type="danger" 
                          text
                          @click="removeMap(index, mapIndex)"
                        >
                          <el-icon><Close /></el-icon>
                        </el-button>
                      </div>
                      <div v-if="env.maps.length === 0" class="env-maps-empty">
                        暂无地图，点击"添加地图"开始配置
                      </div>
                    </div>
                  </div>
                </div>
                <div v-if="presets.environments.length === 0" class="preset-empty">
                  暂无环境，点击"添加环境"开始配置
                </div>
              </div>
              
              <!-- 查看模式 -->
              <div v-else class="env-view-list">
                <div v-for="(env, index) in presets.environments" :key="index" class="env-view-item">
                  <div class="env-view-header">
                    <div class="env-view-name">{{ env.name }}</div>
                    <div class="env-view-count">{{ env.maps.length }} 个地图</div>
                  </div>
                  <div class="env-view-maps">
                    <div 
                      v-for="(map, mapIndex) in env.maps" 
                      :key="mapIndex" 
                      class="env-view-map-item"
                    >
                      {{ map }}
                    </div>
                    <div v-if="env.maps.length === 0" class="env-view-maps-empty">
                      暂无地图
                    </div>
                  </div>
                </div>
                <div v-if="presets.environments.length === 0" class="preset-empty">
                  暂无环境配置
                </div>
              </div>
            </div>
            
            <div style="background: #f5f7fa; padding: 12px; border-radius: 4px; font-size: 13px; color: #606266; line-height: 1.6; margin-top: 20px;">
              <strong>💡 使用说明：</strong><br>
              • 算法：配置常用的算法名称，如 QMIX、QPLEX 等<br>
              • 环境：配置环境名称及其对应的地图列表<br>
              • 创建实验时可以从下拉列表快速选择，也支持输入自定义内容
            </div>
          </el-card>
        </div>
        
        <!-- 模块配置 -->
        <div v-if="activeTab === 'notebook'">
          <!-- 新建实验页模块配置 -->
          <el-card style="margin-bottom: 20px;">
            <template #header>
              <div class="card-header">
                <span class="card-title">📋 新建实验页模块配置</span>
                <div style="display: flex; gap: 8px;">
                  <el-button v-if="!isEditingNewExpModules" size="small" @click="enableNewExpModulesEdit">
                    <el-icon><Edit /></el-icon>
                    编辑
                  </el-button>
                  <template v-else>
                    <el-button size="small" @click="cancelNewExpModulesEdit">
                      <el-icon><Close /></el-icon>
                      取消
                    </el-button>
                    <el-button type="primary" size="small" @click="saveNewExpModulesConfig">
                      <el-icon><Check /></el-icon>
                      保存
                    </el-button>
                  </template>
                </div>
              </div>
            </template>
            
            <el-alert
              title="自定义新建实验页显示的模块，可以启用/禁用模块或调整显示顺序"
              type="info"
              :closable="false"
              style="margin-bottom: 20px;"
            />
            
            <div class="module-list">
              <div 
                v-for="(module, index) in newExpModules" 
                :key="module.id"
                class="module-item"
              >
                <div class="module-info">
                  <el-checkbox 
                    v-model="module.enabled" 
                    :disabled="!isEditingNewExpModules"
                    size="large"
                  >
                    <span style="font-size: 15px; font-weight: 500;">{{ module.name }}</span>
                  </el-checkbox>
                </div>
                <div class="module-actions" v-if="isEditingNewExpModules">
                  <el-button 
                    size="small" 
                    :disabled="index === 0"
                    @click="moveNewExpModule(index, -1)"
                  >
                    <el-icon><ArrowUp /></el-icon>
                  </el-button>
                  <el-button 
                    size="small"
                    :disabled="index === newExpModules.length - 1"
                    @click="moveNewExpModule(index, 1)"
                  >
                    <el-icon><ArrowDown /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
            
            <div style="background: #f5f7fa; padding: 12px; border-radius: 4px; font-size: 13px; color: #606266; line-height: 1.6; margin-top: 20px;">
              <strong>说明：</strong><br>
              • 勾选的模块会在新建实验页显示<br>
              • 使用上下箭头调整模块的显示顺序<br>
              • 配置会自动保存到浏览器本地存储
            </div>
          </el-card>
          
          <!-- 笔记模块配置 -->
          <el-card style="margin-bottom: 20px;">
            <template #header>
              <div class="card-header">
                <span class="card-title">📝 实验详情页模块配置</span>
                <div style="display: flex; gap: 8px;">
                  <el-button v-if="!isEditingNotebook" size="small" @click="enableNotebookEdit">
                    <el-icon><Edit /></el-icon>
                    编辑
                  </el-button>
                  <template v-else>
                    <el-button size="small" @click="cancelNotebookEdit">
                      <el-icon><Close /></el-icon>
                      取消
                    </el-button>
                    <el-button type="primary" size="small" @click="saveNotebookConfig">
                      <el-icon><Check /></el-icon>
                      保存
                    </el-button>
                  </template>
                </div>
              </div>
            </template>
            
            <el-alert
              title="自定义实验详情页显示的模块，可以启用/禁用模块或调整显示顺序"
              type="info"
              :closable="false"
              style="margin-bottom: 20px;"
            />
            
            <div class="module-list">
              <div 
                v-for="(module, index) in notebookModules" 
                :key="module.id"
                class="module-item"
              >
                <div class="module-info">
                  <el-checkbox 
                    v-model="module.enabled" 
                    :disabled="!isEditingNotebook"
                    size="large"
                  >
                    <span style="font-size: 15px; font-weight: 500;">{{ module.name }}</span>
                  </el-checkbox>
                </div>
                <div class="module-actions" v-if="isEditingNotebook">
                  <el-button 
                    size="small" 
                    :disabled="index === 0"
                    @click="moveModule(index, -1)"
                  >
                    <el-icon><ArrowUp /></el-icon>
                  </el-button>
                  <el-button 
                    size="small"
                    :disabled="index === notebookModules.length - 1"
                    @click="moveModule(index, 1)"
                  >
                    <el-icon><ArrowDown /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
            
            <div style="background: #f5f7fa; padding: 12px; border-radius: 4px; font-size: 13px; color: #606266; line-height: 1.6; margin-top: 20px;">
              <strong>说明：</strong><br>
              • 勾选的模块会在实验详情页显示<br>
              • 使用上下箭头调整模块的显示顺序<br>
              • 配置会自动保存到浏览器本地存储
            </div>
          </el-card>
          
          <!-- 标签配置 -->
          <el-card>
            <template #header>
              <div class="card-header">
                <span class="card-title">🏷️ 实验标签配置</span>
                <div style="display: flex; gap: 8px;">
                  <el-button v-if="!isEditingTags" size="small" @click="enableTagsEdit">
                    <el-icon><Edit /></el-icon>
                    编辑
                  </el-button>
                  <template v-else>
                    <el-button size="small" @click="cancelTagsEdit">
                      <el-icon><Close /></el-icon>
                      取消
                    </el-button>
                    <el-button type="primary" size="small" @click="saveTagsConfig">
                      <el-icon><Check /></el-icon>
                      保存
                    </el-button>
                  </template>
                </div>
              </div>
            </template>
            
            <el-alert
              title="配置常用的实验标签，创建实验时可以快速选择"
              type="info"
              :closable="false"
              style="margin-bottom: 20px;"
            />
            
            <div class="preset-section">
              <div class="preset-section-title">
                <el-icon><Collection /></el-icon>
                <span>标签列表</span>
                <el-button v-if="isEditingTags" size="small" @click="addTag">
                  <el-icon><CirclePlus /></el-icon>
                  添加标签
                </el-button>
              </div>
              
              <!-- 编辑模式 -->
              <div v-if="isEditingTags" class="algo-edit-list">
                <div v-for="(tag, index) in experimentTags" :key="index" class="algo-edit-item">
                  <el-input 
                    v-model="experimentTags[index]" 
                    placeholder="如: baseline"
                    size="default"
                  />
                  <el-button 
                    size="small" 
                    type="danger" 
                    text
                    @click="removeTag(index)"
                  >
                    <el-icon><Close /></el-icon>
                  </el-button>
                </div>
                <div v-if="experimentTags.length === 0" class="preset-empty">
                  暂无标签，点击"添加标签"开始配置
                </div>
              </div>
              
              <!-- 查看模式 -->
              <div v-else class="algo-view-list">
                <div v-for="(tag, index) in experimentTags" :key="index" class="algo-view-item">
                  {{ tag }}
                </div>
                <div v-if="experimentTags.length === 0" class="preset-empty">
                  暂无标签配置
                </div>
              </div>
            </div>
            
            <div style="background: #f5f7fa; padding: 12px; border-radius: 4px; font-size: 13px; color: #606266; line-height: 1.6; margin-top: 20px;">
              <strong>💡 使用说明：</strong><br>
              • 标签：配置常用的标签名称，如 baseline、ablation、final 等<br>
              • 创建实验时只能从列表中选择标签
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CopyDocument, Reading, Setting, Document, Key, Edit, Check, Close, ArrowUp, ArrowDown, Collection, CirclePlus, Delete, Cpu, MapLocation, Location, ArrowRight } from '@element-plus/icons-vue'

const API_BASE = 'http://localhost:5001/api'

const activeTab = ref('tutorial')
const configOs = ref('linux')
const keygenOs = ref('linux')
const connectionType = ref('ssh_config')

// 教程参数
const tutorialParams = ref({
  serverAlias: 'LabServer',
  serverIp: '192.168.1.100',
  username: 'server-username',
  port: '22',
  jumpUser: 'jumphost-username',
  jumpHost: '100.127.249.40'
})

const isEditingParams = ref(false)
const originalParams = ref(null)

// 常用配置
const presets = ref({
  algorithms: [],
  environments: []  // 格式：[{ name: 'sc2', maps: ['3m', '8m', '2s3z'] }]
})

const isEditingPresets = ref(false)
const originalPresets = ref(null)

// 笔记模块配置
const notebookModules = ref([
  { id: 'config', name: '实验配置', enabled: true, order: 1 },
  { id: 'tensorboard', name: 'TensorBoard', enabled: true, order: 2 },
  { id: 'description', name: '实验描述', enabled: true, order: 3 },
  { id: 'purpose', name: '实验目的', enabled: true, order: 4 },
  { id: 'observations', name: '观察记录', enabled: true, order: 5 },
  { id: 'results', name: '结果数据', enabled: true, order: 6 },
  { id: 'conclusion', name: '结论与下一步', enabled: true, order: 7 }
])

const isEditingNotebook = ref(false)
const originalNotebookModules = ref(null)

// 新建实验页模块配置
const newExpModules = ref([
  { id: 'config', name: '实验配置', enabled: true, order: 1 },
  { id: 'description', name: '实验描述', enabled: true, order: 2 },
  { id: 'purpose', name: '实验目的', enabled: true, order: 3 }
])

const isEditingNewExpModules = ref(false)
const originalNewExpModules = ref(null)

// 标签配置
const experimentTags = ref([])
const isEditingTags = ref(false)
const originalTags = ref(null)

const config = ref({
  mode: 'local',
  remote: {
    host: '',
    user: '',
    port: 22,
    tensorboard_base_path: '',
    conda_env: '',
    tensorboard_cmd: '',
    tensorboard_param_name: 'local_results_path'
  }
})

// 为不同连接方式维护独立的配置
const directConfig = ref({
  host: '',
  user: '',
  port: 22,
  tensorboard_base_path: '',
  tensorboard_cmd: '',
  tensorboard_param_name: 'local_results_path'
})

const sshConfigConfig = ref({
  host: '',
  tensorboard_base_path: '',
  tensorboard_cmd: '',
  tensorboard_param_name: 'local_results_path'
})

// 本地 TensorBoard 配置
const localTensorboardConfig = ref({
  enabled: true,
  command: 'tensorboard'
})

const saving = ref(false)
const isEditing = ref(false)

const testCommand = computed(() => {
  if (config.value.mode === 'remote') {
    if (connectionType.value === 'ssh_config') {
      const host = sshConfigConfig.value.host
      if (!host) {
        return '请先填写主机别名'
      }
      return `ssh ${host}`
    } else {
      const { host, user, port } = directConfig.value
      if (!host || !user) {
        return '请先填写服务器地址和用户名'
      }
      const portArg = port !== 22 ? ` -p ${port}` : ''
      return `ssh ${user}@${host}${portArg}`
    }
  }
  
  return '本地模式无需测试连接'
})

const handleTabChange = (index) => {
  activeTab.value = index
}

const loadConfig = async () => {
  try {
    const { data } = await axios.get(`${API_BASE}/config`)
    
    // 根据后端返回的 mode 设置前端的显示模式
    if (data.mode === 'ssh_config') {
      config.value.mode = 'remote'  // 前端统一显示为远程模式
      connectionType.value = 'ssh_config'
      sshConfigConfig.value = {
        host: data.remote.host || '',
        tensorboard_base_path: data.remote.tensorboard_base_path || '',
        tensorboard_cmd: data.remote.tensorboard_cmd || '',
        tensorboard_param_name: data.remote.tensorboard_param_name || 'local_results_path'
      }
    } else if (data.mode === 'remote') {
      config.value.mode = 'remote'  // 前端统一显示为远程模式
      connectionType.value = 'direct'
      directConfig.value = {
        host: data.remote.host || '',
        user: data.remote.user || '',
        port: data.remote.port || 22,
        tensorboard_base_path: data.remote.tensorboard_base_path || '',
        tensorboard_cmd: data.remote.tensorboard_cmd || '',
        tensorboard_param_name: data.remote.tensorboard_param_name || 'local_results_path'
      }
    } else {
      // 本地模式
      config.value.mode = 'local'
      connectionType.value = 'ssh_config'  // 默认连接方式
    }
    
    // 加载本地 TensorBoard 配置
    if (data.local_tensorboard) {
      localTensorboardConfig.value = {
        enabled: data.local_tensorboard.enabled !== false,  // 默认启用
        command: data.local_tensorboard.command || 'tensorboard'
      }
    }
    
    if (data.remote.host || data.mode === 'remote' || data.mode === 'ssh_config') {
      isEditing.value = false
    } else {
      isEditing.value = true
    }
  } catch (error) {
    ElMessage.error('加载配置失败')
    isEditing.value = true
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    const configToSave = {
      mode: config.value.mode,
      remote: {},
      local_tensorboard: {
        enabled: localTensorboardConfig.value.enabled,
        command: localTensorboardConfig.value.command || 'tensorboard'
      }
    }
    
    if (config.value.mode === 'remote') {
      if (connectionType.value === 'ssh_config') {
        // SSH Config 模式
        configToSave.mode = 'ssh_config'
        configToSave.remote = {
          host: sshConfigConfig.value.host,
          user: '',
          port: 22,
          tensorboard_base_path: sshConfigConfig.value.tensorboard_base_path,
          tensorboard_cmd: sshConfigConfig.value.tensorboard_cmd,
          tensorboard_param_name: sshConfigConfig.value.tensorboard_param_name || 'local_results_path'
        }
      } else {
        // 直接连接模式
        configToSave.mode = 'remote'
        configToSave.remote = {
          host: directConfig.value.host,
          user: directConfig.value.user,
          port: directConfig.value.port,
          tensorboard_base_path: directConfig.value.tensorboard_base_path,
          tensorboard_cmd: directConfig.value.tensorboard_cmd,
          tensorboard_param_name: directConfig.value.tensorboard_param_name || 'local_results_path'
        }
      }
    } else {
      // 本地模式
      configToSave.remote = {
        host: '',
        user: '',
        port: 22,
        tensorboard_base_path: '',
        tensorboard_cmd: ''
      }
    }
    
    await axios.post(`${API_BASE}/config`, configToSave)
    ElMessage.success('配置已保存')
    isEditing.value = false
  } catch (error) {
    ElMessage.error('保存配置失败')
  } finally {
    saving.value = false
  }
}

const enableEdit = () => {
  isEditing.value = true
}

const copyCommand = async () => {
  try {
    await navigator.clipboard.writeText(testCommand.value)
    ElMessage.success('命令已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

const copySshKeygen = () => {
  copyToClipboard('ssh-keygen -t rsa -b 4096')
}

const copyWindowsSshCopyId = () => {
  copyToClipboard(`type $env:USERPROFILE\\.ssh\\id_rsa.pub | ssh ${tutorialParams.value.username}@${tutorialParams.value.serverIp} "cat >> ~/.ssh/authorized_keys"`)
}

const copyServerSetup = () => {
  copyToClipboard('mkdir -p ~/.ssh\necho "粘贴你的公钥内容" >> ~/.ssh/authorized_keys\nchmod 700 ~/.ssh\nchmod 600 ~/.ssh/authorized_keys')
}

const enableParamsEdit = () => {
  originalParams.value = JSON.parse(JSON.stringify(tutorialParams.value))
  isEditingParams.value = true
}

const cancelParamsEdit = () => {
  if (originalParams.value) {
    tutorialParams.value = JSON.parse(JSON.stringify(originalParams.value))
  }
  isEditingParams.value = false
}

const saveParams = () => {
  isEditingParams.value = false
  ElMessage.success('参数已保存')
}

const enableNotebookEdit = () => {
  originalNotebookModules.value = JSON.parse(JSON.stringify(notebookModules.value))
  isEditingNotebook.value = true
}

const cancelNotebookEdit = () => {
  if (originalNotebookModules.value) {
    notebookModules.value = JSON.parse(JSON.stringify(originalNotebookModules.value))
  }
  isEditingNotebook.value = false
}

const saveNotebookConfig = () => {
  // 这里可以将配置保存到 localStorage 或后端
  localStorage.setItem('notebookModules', JSON.stringify(notebookModules.value))
  isEditingNotebook.value = false
  ElMessage.success('笔记配置已保存')
}

const moveModule = (index, direction) => {
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= notebookModules.value.length) return
  
  const temp = notebookModules.value[index]
  notebookModules.value[index] = notebookModules.value[newIndex]
  notebookModules.value[newIndex] = temp
  
  // 更新 order
  notebookModules.value.forEach((module, idx) => {
    module.order = idx + 1
  })
}

// 常用配置管理
const addAlgorithm = () => {
  presets.value.algorithms.push('')
}

const removeAlgorithm = (index) => {
  presets.value.algorithms.splice(index, 1)
}

const addEnvironment = () => {
  presets.value.environments.push({
    name: '',
    maps: [],
    expanded: true  // 新添加的环境默认展开
  })
}

const removeEnvironment = (index) => {
  presets.value.environments.splice(index, 1)
}

const toggleEnvExpand = (index) => {
  presets.value.environments[index].expanded = !presets.value.environments[index].expanded
}

const confirmRemoveEnvironment = (index) => {
  const envName = presets.value.environments[index].name || '未命名环境'
  ElMessageBox.confirm(
    `确定要删除环境"${envName}"及其所有地图配置吗？`,
    '确认删除',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    removeEnvironment(index)
    ElMessage.success('删除成功')
  }).catch(() => {
    // 用户取消删除
  })
}

const addMap = (envIndex) => {
  presets.value.environments[envIndex].maps.push('')
}

const removeMap = (envIndex, mapIndex) => {
  presets.value.environments[envIndex].maps.splice(mapIndex, 1)
}

const enablePresetsEdit = () => {
  originalPresets.value = JSON.parse(JSON.stringify(presets.value))
  isEditingPresets.value = true
}

const cancelPresetsEdit = () => {
  if (originalPresets.value) {
    presets.value = JSON.parse(JSON.stringify(originalPresets.value))
  }
  isEditingPresets.value = false
}

const savePresetsConfig = () => {
  // 过滤空值
  presets.value.algorithms = presets.value.algorithms.filter(a => a.trim() !== '')
  presets.value.environments = presets.value.environments
    .filter(e => e.name && e.name.trim() !== '')
    .map(e => ({
      name: e.name.trim(),
      maps: e.maps.filter(m => m && m.trim() !== '').map(m => m.trim())
    }))
  
  // 保存到 localStorage
  localStorage.setItem('experimentPresets', JSON.stringify(presets.value))
  isEditingPresets.value = false
  ElMessage.success('常用配置已保存')
}

const loadPresetsConfig = () => {
  const saved = localStorage.getItem('experimentPresets')
  if (saved) {
    try {
      const loaded = JSON.parse(saved)
      // 兼容旧格式（environments 是字符串数组）
      if (loaded.environments && loaded.environments.length > 0) {
        if (typeof loaded.environments[0] === 'string') {
          // 旧格式，转换为新格式
          loaded.environments = loaded.environments.map(name => ({
            name: name,
            maps: [],
            expanded: false
          }))
        } else {
          // 新格式，确保有 expanded 属性
          loaded.environments = loaded.environments.map(env => ({
            ...env,
            expanded: env.expanded !== undefined ? env.expanded : false
          }))
        }
      }
      presets.value = loaded
    } catch (e) {
      console.error('加载常用配置失败', e)
    }
  }
}

const loadNotebookConfig = () => {
  const saved = localStorage.getItem('notebookModules')
  if (saved) {
    try {
      notebookModules.value = JSON.parse(saved)
    } catch (e) {
      console.error('加载笔记配置失败', e)
    }
  }
}

const loadNewExpModulesConfig = () => {
  const saved = localStorage.getItem('newExpModules')
  if (saved) {
    try {
      newExpModules.value = JSON.parse(saved)
    } catch (e) {
      console.error('加载新建实验页模块配置失败', e)
    }
  }
}

const loadTagsConfig = () => {
  const saved = localStorage.getItem('experimentTags')
  if (saved) {
    try {
      experimentTags.value = JSON.parse(saved)
    } catch (e) {
      console.error('加载标签配置失败', e)
    }
  }
}

const enableTagsEdit = () => {
  originalTags.value = JSON.parse(JSON.stringify(experimentTags.value))
  isEditingTags.value = true
}

const cancelTagsEdit = () => {
  if (originalTags.value) {
    experimentTags.value = JSON.parse(JSON.stringify(originalTags.value))
  }
  isEditingTags.value = false
}

const saveTagsConfig = () => {
  // 过滤空值
  experimentTags.value = experimentTags.value.filter(t => t && t.trim() !== '').map(t => t.trim())
  
  // 保存到 localStorage
  localStorage.setItem('experimentTags', JSON.stringify(experimentTags.value))
  isEditingTags.value = false
  ElMessage.success('标签配置已保存')
}

const addTag = () => {
  experimentTags.value.push('')
}

const removeTag = (index) => {
  experimentTags.value.splice(index, 1)
}

const enableNewExpModulesEdit = () => {
  originalNewExpModules.value = JSON.parse(JSON.stringify(newExpModules.value))
  isEditingNewExpModules.value = true
}

const cancelNewExpModulesEdit = () => {
  if (originalNewExpModules.value) {
    newExpModules.value = JSON.parse(JSON.stringify(originalNewExpModules.value))
  }
  isEditingNewExpModules.value = false
}

const saveNewExpModulesConfig = () => {
  // 保存到 localStorage
  localStorage.setItem('newExpModules', JSON.stringify(newExpModules.value))
  isEditingNewExpModules.value = false
  ElMessage.success('新建实验页模块配置已保存')
}

const moveNewExpModule = (index, direction) => {
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= newExpModules.value.length) return
  
  const temp = newExpModules.value[index]
  newExpModules.value[index] = newExpModules.value[newIndex]
  newExpModules.value[newIndex] = temp
  
  // 更新 order
  newExpModules.value.forEach((module, idx) => {
    module.order = idx + 1
  })
}

onMounted(() => {
  loadConfig()
  loadNotebookConfig()
  loadPresetsConfig()
  loadNewExpModulesConfig()
  loadTagsConfig()
})
</script>

<style scoped>
.settings-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.settings-layout {
  display: flex;
  gap: 20px;
}

.settings-sidebar {
  width: 220px;
  flex-shrink: 0;
}

.settings-sidebar .el-menu {
  border-radius: 8px;
}

.settings-content {
  flex: 1;
  min-width: 0;
}

.tutorial-section {
  width: 100%;
}

.tutorial-block {
  margin-bottom: 32px;
}

.tutorial-block:last-child {
  margin-bottom: 0;
}

.tutorial-block h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.tutorial-block h3 .el-icon {
  font-size: 20px;
  color: #409eff;
}

.tutorial-desc {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 16px;
}

.tutorial-content {
  padding: 16px;
}

.tutorial-content h4 {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin: 16px 0 12px 0;
}

.tutorial-content h4:first-child {
  margin-top: 0;
}

.code-block {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  color: #303133;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 8px 0;
  overflow-x: auto;
}

.tip {
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
  margin: 8px 0;
}

.tip code {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 12px;
  color: #e6a23c;
}

.warning-box {
  background: #fef0f0;
  border: 1px solid #fde2e2;
  border-radius: 4px;
  padding: 12px;
  margin-top: 16px;
  font-size: 13px;
  color: #f56c6c;
  line-height: 1.8;
}

.warning-box code {
  background: #fff;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 12px;
  color: #f56c6c;
}

.params-config {
  background: #f9fafb;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}

.param-section {
  margin-bottom: 20px;
}

.param-section:last-child {
  margin-bottom: 0;
}

.param-section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
}

.code-block-wrapper {
  position: relative;
  margin: 8px 0;
}

.code-block-wrapper .copy-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.code-block-wrapper:hover .copy-btn {
  opacity: 1;
}

.module-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.module-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f9fafb;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  transition: all 0.2s;
}

.module-item:hover {
  background: #f5f7fa;
  border-color: #d0d4d9;
}

.module-info {
  flex: 1;
}

.module-actions {
  display: flex;
  gap: 8px;
}

.preset-section {
  margin-bottom: 32px;
}

.preset-section:last-child {
  margin-bottom: 0;
}

.preset-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.preset-section-title .el-icon {
  font-size: 18px;
  color: #409eff;
}

.preset-section-title .el-button {
  margin-left: auto;
}

.preset-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  min-height: 60px;
}

.preset-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.preset-item .el-input {
  width: 150px;
}

.preset-empty {
  width: 100%;
  text-align: center;
  padding: 20px;
  color: #9ca3af;
  font-size: 14px;
  background: #f9fafb;
  border-radius: 6px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 算法配置样式 */
.algo-edit-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 8px;
}

.algo-edit-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 6px 8px;
  transition: all 0.2s;
}

.algo-edit-item:hover {
  border-color: #667eea;
}

.algo-edit-item .el-input {
  flex: 1;
}

.algo-edit-item .el-input :deep(.el-input__wrapper) {
  background: transparent;
  border: none;
  box-shadow: none;
}

.algo-edit-item .el-input :deep(.el-input__inner) {
  font-weight: 500;
  color: #667eea;
}

.algo-view-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
}

.algo-view-item {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  text-align: center;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
  transition: all 0.2s;
}

.algo-view-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* 环境配置样式 - 编辑模式 */
.env-edit-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.env-edit-item {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
}

.env-edit-item:hover {
  border-color: #10b981;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.1);
}

.env-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
}

.env-item-header:hover {
  background: #f9fafb;
}

.env-item-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.expand-icon {
  color: #9ca3af;
  transition: transform 0.2s;
  flex-shrink: 0;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.env-name-input-inline {
  max-width: 200px;
}

.env-name-input-inline :deep(.el-input__wrapper) {
  background: transparent;
  border: 1px solid transparent;
  box-shadow: none;
  transition: all 0.2s;
}

.env-name-input-inline :deep(.el-input__wrapper):hover {
  border-color: #e5e7eb;
  background: #f9fafb;
}

.env-name-input-inline :deep(.el-input__wrapper.is-focus) {
  border-color: #10b981;
  background: white;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.env-name-input-inline :deep(.el-input__inner) {
  font-weight: 500;
  color: #10b981;
}

.env-map-count {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 4px 10px;
  border-radius: 12px;
  white-space: nowrap;
}

.env-maps-content {
  padding: 0 16px 16px 16px;
  border-top: 1px solid #f3f4f6;
  background: #fafbfc;
}

.env-maps-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
}

.maps-label {
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
}

.env-maps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 8px;
}

.map-edit-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 6px 8px;
  transition: all 0.2s;
}

.map-edit-item:hover {
  border-color: #10b981;
}

.map-edit-item .el-input {
  flex: 1;
}

.map-edit-item .el-input :deep(.el-input__wrapper) {
  background: transparent;
  border: none;
  box-shadow: none;
}

.map-edit-item .el-input :deep(.el-input__inner) {
  color: #166534;
  font-weight: 500;
}

.env-maps-empty {
  text-align: center;
  padding: 24px;
  color: #9ca3af;
  font-size: 13px;
  background: white;
  border: 2px dashed #e5e7eb;
  border-radius: 6px;
  grid-column: 1 / -1;
}

/* 环境配置样式 - 查看模式 */
.env-view-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.env-view-item {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
}

.env-view-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.env-view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f3f4f6;
}

.env-view-name {
  font-size: 16px;
  font-weight: 600;
  color: #10b981;
}

.env-view-count {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 4px 10px;
  border-radius: 12px;
}

.env-view-maps {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 8px;
}

.env-view-map-item {
  background: #f0fdf4;
  color: #166534;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  text-align: center;
  border: 1px solid #bbf7d0;
  transition: all 0.2s;
}

.env-view-map-item:hover {
  background: #dcfce7;
  border-color: #86efac;
}

.env-view-maps-empty {
  font-size: 13px;
  color: #9ca3af;
  text-align: center;
  padding: 12px;
  grid-column: 1 / -1;
}

/* 标签配置样式 */
.tags-display-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.tag-item-hover {
  position: relative;
  padding-right: 28px;
  cursor: default;
  transition: all 0.2s;
}

.tag-item-hover:hover {
  padding-right: 32px;
}

.tag-delete-icon {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  color: #f56c6c;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.tag-delete-icon:hover {
  color: #f56c6c;
  transform: translateY(-50%) scale(1.2);
}

.tags-edit-section {
  width: 100%;
}

.tags-edit-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tag-edit-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  transition: all 0.2s;
}

.tag-edit-item:hover {
  border-color: #667eea;
}

.tag-edit-item .el-input {
  flex: 1;
}

.tags-view-section {
  width: 100%;
}

.tags-view-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tags-empty {
  text-align: center;
  padding: 40px 20px;
  color: #9ca3af;
  font-size: 14px;
}

</style>
