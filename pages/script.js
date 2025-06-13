document.addEventListener('DOMContentLoaded', function() {
    // Enhanced smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            if (targetSection) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = targetSection.offsetTop - headerHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Enhanced scroll animations with staggered effects
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('fade-in');
                }, index * 100);
            }
        });
    }, observerOptions);

    // Observe all sections and cards
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        observer.observe(section);
    });

    const cards = document.querySelectorAll('.feature-card, .domain-card, .rule-card, .doc-card, .step-content');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        observer.observe(card);
    });

    // Enhanced copy code functionality
    const codeBlock = document.querySelector('.config-example pre code');
    if (codeBlock) {
        const copyButton = document.createElement('button');
        copyButton.innerHTML = '📋 复制代码';
        copyButton.className = 'copy-btn';
        copyButton.style.cssText = `
            position: absolute;
            top: 16px;
            right: 16px;
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.8rem;
            font-weight: 600;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: var(--shadow);
        `;
        
        copyButton.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = 'var(--shadow-lg)';
        });
        
        copyButton.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'var(--shadow)';
        });
        
        copyButton.addEventListener('click', function() {
            navigator.clipboard.writeText(codeBlock.textContent).then(() => {
                copyButton.innerHTML = '✅ 已复制!';
                copyButton.style.background = 'var(--success-color)';
                setTimeout(() => {
                    copyButton.innerHTML = '📋 复制代码';
                    copyButton.style.background = 'var(--primary-color)';
                }, 2000);
            });
        });

        const preElement = codeBlock.parentElement;
        preElement.style.position = 'relative';
        preElement.appendChild(copyButton);
    }

    // Enhanced header scroll effect
    const header = document.querySelector('.header');
    let lastScrollTop = 0;
    let scrollTimer = null;

    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Add scrolled class for backdrop effect
        if (scrollTop > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
        
        // Hide/show header based on scroll direction
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            header.style.transform = 'translateY(-100%)';
        } else {
            header.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = scrollTop;
        
        // Clear existing timer
        if (scrollTimer) {
            clearTimeout(scrollTimer);
        }
        
        // Set timer to show header after scroll stops
        scrollTimer = setTimeout(() => {
            header.style.transform = 'translateY(0)';
        }, 150);
    });

    // Add transition to header
    header.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';

    // Parallax effect for hero section
    const hero = document.querySelector('.hero');
    if (hero) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const parallax = scrolled * 0.5;
            hero.style.transform = `translateY(${parallax}px)`;
        });
    }

    // Add floating animation to feature icons
    const featureIcons = document.querySelectorAll('.feature-icon');
    featureIcons.forEach((icon, index) => {
        icon.style.animation = `float 3s ease-in-out infinite ${index * 0.5}s`;
    });

    // Enhanced mobile menu with animations
    function initMobileMenu() {
        const nav = document.querySelector('.nav');
        const toggleButton = document.createElement('button');
        toggleButton.className = 'mobile-menu-toggle';
        toggleButton.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        toggleButton.style.display = 'none';
        
        const style = document.createElement('style');
        style.textContent = `
            @media (max-width: 768px) {
                .mobile-menu-toggle {
                    display: flex !important;
                    flex-direction: column;
                    justify-content: space-around;
                    width: 30px;
                    height: 30px;
                    background: none;
                    border: none;
                    cursor: pointer;
                    padding: 0;
                }
                
                .mobile-menu-toggle span {
                    width: 100%;
                    height: 3px;
                    background: var(--text-color);
                    border-radius: 2px;
                    transition: all 0.3s ease;
                }
                
                .mobile-menu-toggle.active span:nth-child(1) {
                    transform: rotate(45deg) translate(7px, 7px);
                }
                
                .mobile-menu-toggle.active span:nth-child(2) {
                    opacity: 0;
                }
                
                .mobile-menu-toggle.active span:nth-child(3) {
                    transform: rotate(-45deg) translate(7px, -7px);
                }
                
                .nav {
                    display: none;
                    position: absolute;
                    top: 100%;
                    left: 0;
                    right: 0;
                    background: rgba(255, 255, 255, 0.98);
                    backdrop-filter: blur(20px);
                    box-shadow: var(--shadow-lg);
                    flex-direction: column;
                    padding: 2rem;
                    gap: 1rem;
                    border-top: 1px solid var(--border-light);
                    animation: slideDown 0.3s ease-out;
                }
                
                .nav.active {
                    display: flex;
                }
                
                .nav a {
                    padding: 1rem;
                    margin: 0;
                    border-radius: var(--border-radius-sm);
                    text-align: center;
                    background: var(--bg-light);
                    border: 1px solid var(--border-light);
                }
                
                @keyframes slideDown {
                    from {
                        opacity: 0;
                        transform: translateY(-20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            }
        `;
        document.head.appendChild(style);
        
        toggleButton.addEventListener('click', function() {
            nav.classList.toggle('active');
            toggleButton.classList.toggle('active');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!header.contains(e.target)) {
                nav.classList.remove('active');
                toggleButton.classList.remove('active');
            }
        });
        
        header.querySelector('.container').appendChild(toggleButton);
    }

    initMobileMenu();

    // Add typing animation to hero title
    const heroTitle = document.querySelector('.hero h2');
    if (heroTitle) {
        const text = heroTitle.textContent;
        heroTitle.textContent = '';
        heroTitle.style.borderRight = '2px solid rgba(255,255,255,0.8)';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                heroTitle.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            } else {
                setTimeout(() => {
                    heroTitle.style.borderRight = 'none';
                }, 1000);
            }
        };
        
        // Start typing after page load
        setTimeout(typeWriter, 1000);
    }

    // Add pulse animation to CTA buttons
    const ctaButtons = document.querySelectorAll('.btn-primary');
    ctaButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.animation = 'pulse 0.6s ease-in-out';
        });
        
        button.addEventListener('animationend', function() {
            this.style.animation = '';
        });
    });

    // Add progress indicator for long content
    const progressBar = document.createElement('div');
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        height: 3px;
        background: var(--bg-gradient);
        z-index: 1001;
        transition: width 0.3s ease;
        border-radius: 0 3px 3px 0;
    `;
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', function() {
        const scrolled = (window.pageYOffset / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
        progressBar.style.width = scrolled + '%';
    });

    // 子域名检测功能
    initSubdomainChecker();
});

// 子域名检测功能
function initSubdomainChecker() {
    const subdomainInput = document.getElementById('subdomainInput');
    const checkButton = document.getElementById('checkButton');
    const checkerResult = document.getElementById('checkerResult');
    const totalDomainsSpan = document.getElementById('totalDomains');
    const recentDomainsList = document.getElementById('recentDomainsList');
    const domainSelect = document.getElementById('domainSelect');
    const domainSuffix = document.getElementById('domainSuffix');
    
    let registeredDomains = new Map(); // 改为 Map，按域名分组存储
    let reservedSubdomains = new Set([
        '@', 'www', 'mail', 'email', 'webmail', 'ns', 'dns',
        'api', 'cdn', 'ftp', 'sftp', 'admin', 'panel', 
        'dashboard', 'control', 'dev', 'test', 'staging', 
        'demo', 'blog', 'forum', 'wiki', 'docs', 'tv',
        'app', 'mobile', 'static', 'assets'
    ]);

    // 域名配置
    const domainConfig = {
        'ciao.su': { enabled: true, path: 'ciao.su' },
        'ciallo.de': { enabled: false, path: 'ciallo.de' }
    };

    // 检查是否支持必要的 API
    if (!window.fetch) {
        console.warn('Fetch API not supported, subdomain checker will be limited');
        recentDomainsList.innerHTML = `
            <div class="error-message">
                您的浏览器不支持此功能，请使用现代浏览器
            </div>
        `;
        return;
    }

    // 域名选择器事件
    domainSelect.addEventListener('change', function() {
        const selectedDomain = this.value;
        const isEnabled = domainConfig[selectedDomain]?.enabled;
        
        // 更新后缀显示
        domainSuffix.textContent = '.' + selectedDomain;
        
        // 更新样式
        if (isEnabled) {
            domainSuffix.classList.remove('paused');
            checkButton.disabled = false;
        } else {
            domainSuffix.classList.add('paused');
            checkButton.disabled = true;
        }
        
        // 清除之前的结果
        checkerResult.classList.remove('show');
        
        // 重新加载该域名的数据
        loadRegisteredDomains(selectedDomain);
    });

    // 加载已注册的域名数据
    loadRegisteredDomains();

    // 输入验证
    subdomainInput.addEventListener('input', function() {
        const value = this.value.toLowerCase();
        const isValid = validateSubdomain(value);
        const inputGroup = this.parentElement;
        const validationHint = inputGroup.nextElementSibling;
        const selectedDomain = domainSelect.value;
        const isDomainEnabled = domainConfig[selectedDomain]?.enabled;

        if (value === '') {
            inputGroup.classList.remove('invalid');
            if (validationHint && validationHint.classList.contains('validation-hint')) {
                validationHint.remove();
            }
            checkButton.disabled = !isDomainEnabled;
            return;
        }

        if (isValid && isDomainEnabled) {
            inputGroup.classList.remove('invalid');
            if (validationHint && validationHint.classList.contains('validation-hint')) {
                validationHint.remove();
            }
            checkButton.disabled = false;
        } else {
            inputGroup.classList.add('invalid');
            if (!validationHint || !validationHint.classList.contains('validation-hint')) {
                const hint = document.createElement('div');
                hint.className = 'validation-hint error';
                hint.textContent = !isDomainEnabled ? '所选域名暂停开放申请' : getValidationMessage(value);
                inputGroup.parentElement.insertBefore(hint, inputGroup.nextSibling);
            }
            checkButton.disabled = true;
        }
    });

    // 回车键检测
    subdomainInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !checkButton.disabled) {
            e.preventDefault();
            checkSubdomain();
        }
    });

    // 检测按钮点击
    checkButton.addEventListener('click', checkSubdomain);

    // 验证子域名格式
    function validateSubdomain(subdomain) {
        if (!subdomain) return false;
        if (subdomain.length < 2 || subdomain.length > 63) return false;
        if (subdomain.startsWith('-') || subdomain.endsWith('-')) return false;
        if (!/^[a-z0-9-]+$/.test(subdomain)) return false;
        return true;
    }

    // 获取验证错误信息
    function getValidationMessage(subdomain) {
        if (subdomain.length < 2) return '子域名长度至少2个字符';
        if (subdomain.length > 63) return '子域名长度不能超过63个字符';
        if (subdomain.startsWith('-') || subdomain.endsWith('-')) return '子域名不能以连字符开头或结尾';
        if (!/^[a-z0-9-]+$/.test(subdomain)) return '只能包含小写字母、数字和连字符';
        return '无效的子域名格式';
    }

    // 检测子域名可用性
    async function checkSubdomain() {
        const subdomain = subdomainInput.value.toLowerCase().trim();
        const selectedDomain = domainSelect.value;
        
        if (!validateSubdomain(subdomain)) return;
        
        // 检查域名是否开放
        if (!domainConfig[selectedDomain]?.enabled) {
            showResult('domain-paused', '域名暂停开放', `${selectedDomain} 域名暂时不开放申请`, '请选择其他域名');
            return;
        }

        // 显示加载状态
        checkButton.disabled = true;
        checkButton.classList.add('loading');
        checkButton.textContent = '';
        
        try {
            // 检查是否为保留域名
            if (reservedSubdomains.has(subdomain)) {
                showResult('unavailable', '域名不可用', `"${subdomain}" 是系统保留域名，无法申请`, '保留域名');
                return;
            }

            // 检查是否已被注册
            const domainSet = registeredDomains.get(selectedDomain) || new Set();
            if (domainSet.has(subdomain)) {
                showResult('unavailable', '域名不可用', `"${subdomain}.${selectedDomain}" 已被其他用户注册`, '已注册');
                return;
            }

            // 域名可用
            showResult('available', '域名可用！', `"${subdomain}.${selectedDomain}" 可以申请`, '');

        } catch (error) {
            console.error('检测失败:', error);
            showResult('error', '检测失败', '检测过程中出现错误，但域名可能仍然可用', '请手动确认');
        } finally {
            // 恢复按钮状态
            setTimeout(() => {
                const isDomainEnabled = domainConfig[domainSelect.value]?.enabled;
                checkButton.disabled = !isDomainEnabled || !subdomainInput.value.trim();
                checkButton.classList.remove('loading');
                checkButton.textContent = '检测';
            }, 500);
        }
    }

    // 显示检测结果
    function showResult(type, title, message, details) {
        const resultIcon = checkerResult.querySelector('.result-icon');
        const resultText = checkerResult.querySelector('.result-text');
        const resultDetails = checkerResult.querySelector('.result-details');

        // 设置图标
        const icons = {
            available: '✅',
            unavailable: '❌',
            error: '⚠️',
            'domain-paused': '⏸️'
        };
        resultIcon.textContent = icons[type];

        // 设置文本
        resultText.innerHTML = `
            <h4>${title}</h4>
            <p>${message}</p>
        `;

        // 设置详情
        resultDetails.innerHTML = details || '';

        // 设置样式类
        checkerResult.className = `checker-result show ${type}`;

        // 滚动到结果位置
        setTimeout(() => {
            checkerResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    }

    // 加载已注册的域名数据
    async function loadRegisteredDomains(specificDomain = null) {
        const domainsToLoad = specificDomain ? [specificDomain] : Object.keys(domainConfig);
        
        try {
            // 显示加载状态
            recentDomainsList.innerHTML = '<div class="loading">正在加载域名数据...</div>';
            
            for (const domain of domainsToLoad) {
                const domainPath = domainConfig[domain]?.path || domain;
                const apiUrl = `https://api.github.com/repos/bestzwei/LibreDomains/contents/domains/${domainPath}`;
                
                try {
                    const response = await fetch(apiUrl, {
                        method: 'GET',
                        headers: {
                            'Accept': 'application/vnd.github.v3+json',
                            'User-Agent': 'LibreDomains-Checker/1.0'
                        },
                        cache: 'no-cache'
                    });
                    
                    if (!response.ok) {
                        console.warn(`GitHub API failed for ${domain} with status: ${response.status}`);
                        continue;
                    }
                    
                    const files = await response.json();
                    
                    if (!Array.isArray(files)) {
                        continue;
                    }
                    
                    const domainFiles = files.filter(file => 
                        file.name && 
                        file.name.endsWith('.json') && 
                        file.name !== 'example.json' &&
                        file.type === 'file'
                    );

                    // 存储到对应域名的 Set 中
                    const domainSet = new Set();
                    domainFiles.forEach(file => {
                        const domainName = file.name.replace('.json', '');
                        if (domainName && /^[a-z0-9-]+$/.test(domainName)) {
                            domainSet.add(domainName);
                        }
                    });
                    
                    registeredDomains.set(domain, domainSet);
                    
                } catch (domainError) {
                    console.error(`加载 ${domain} 域名数据失败:`, domainError);
                }
            }

            // 更新显示
            updateDisplay();

        } catch (error) {
            console.error('加载域名数据失败:', error);
            await loadDomainsFromBackup();
        }
    }

    // 更新显示
    function updateDisplay() {
        const selectedDomain = domainSelect.value;
        const currentDomainSet = registeredDomains.get(selectedDomain) || new Set();
        
        // 更新统计信息
        if (totalDomainsSpan) {
            totalDomainsSpan.textContent = currentDomainSet.size;
        }

        // 显示最近注册的域名
        const recentDomains = Array.from(currentDomainSet)
            .sort()
            .slice(0, 12)
            .map(name => ({
                name,
                url: '#',
                size: 0
            }));

        displayRecentDomains(recentDomains);
    }

    // 备用数据加载方案
    async function loadDomainsFromBackup() {
        try {
            const knownDomains = ['cc', 'example'];
            
            registeredDomains.clear();
            const ciaoSuSet = new Set();
            knownDomains.forEach(domain => {
                if (domain !== 'example') {
                    ciaoSuSet.add(domain);
                }
            });
            registeredDomains.set('ciao.su', ciaoSuSet);

            updateDisplay();

            if (recentDomainsList.children.length === 0) {
                recentDomainsList.innerHTML = `
                    <div class="error-message">
                        无法连接到 GitHub API，显示的是缓存数据。
                        <br>完整数据请访问 
                        <a href="https://github.com/bestzwei/LibreDomains/tree/main/domains" 
                           target="_blank" style="color: var(--primary-color);">GitHub 仓库</a>
                    </div>
                `;
            }

        } catch (backupError) {
            console.error('备用数据加载也失败:', backupError);
            if (recentDomainsList) {
                recentDomainsList.innerHTML = `
                    <div class="error-message">
                        数据加载失败，请检查网络连接或稍后重试
                        <br><a href="https://github.com/bestzwei/LibreDomains/tree/main/domains" 
                               target="_blank" style="color: var(--primary-color);">查看完整域名列表</a>
                    </div>
                `;
            }
        }
    }

    // 显示最近注册的域名
    function displayRecentDomains(domains) {
        if (!recentDomainsList) return;

        if (domains.length === 0) {
            recentDomainsList.innerHTML = '<div class="loading">暂无注册域名</div>';
            return;
        }

        const domainsHtml = domains.map(domain => `
            <div class="domain-item" data-domain="${domain.name}">
                <span class="domain-name">${domain.name}</span>
                <div class="domain-status" title="已注册"></div>
            </div>
        `).join('');

        recentDomainsList.innerHTML = domainsHtml;

        // 添加点击效果
        const domainItems = recentDomainsList.querySelectorAll('.domain-item');
        domainItems.forEach(item => {
            item.addEventListener('click', function() {
                const domainName = this.getAttribute('data-domain') || 
                                  this.querySelector('.domain-name')?.textContent;
                
                if (domainName && subdomainInput) {
                    subdomainInput.value = domainName;
                    subdomainInput.focus();
                    
                    // 添加视觉反馈
                    this.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        this.style.transform = '';
                    }, 150);
                    
                    // 自动触发检测
                    setTimeout(() => {
                        if (checkButton && !checkButton.disabled) {
                            checkSubdomain();
                        }
                    }, 200);
                }
            });
        });
    }

    // 初始化时触发域名选择事件
    domainSelect.dispatchEvent(new Event('change'));

    // 减少自动刷新频率以避免API限制
    setInterval(() => loadRegisteredDomains(), 10 * 60 * 1000); // 10分钟
}

// 禁用 Cloudflare RUM 相关错误
window.addEventListener('error', function(e) {
    // 忽略 Cloudflare RUM 相关错误
    if (e.message && e.message.includes('cdn-cgi/rum')) {
        e.preventDefault();
        return false;
    }
});

// 禁用 Cloudflare Web Analytics 如果不需要
if (typeof window.cloudflareAnalytics !== 'undefined') {
    window.cloudflareAnalytics = null;
}

// Add additional CSS animations
const additionalStyles = document.createElement('style');
additionalStyles.textContent = `
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .fade-in {
        opacity: 1 !important;
        transform: translateY(0) !important;
        transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .feature-card:nth-child(odd) {
        animation-delay: 0.1s;
    }
    
    .feature-card:nth-child(even) {
        animation-delay: 0.2s;
    }
`;
document.head.appendChild(additionalStyles);
