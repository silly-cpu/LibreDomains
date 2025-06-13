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
    
    let registeredDomains = new Set();
    let reservedSubdomains = new Set([
        '@', 'www', 'mail', 'email', 'webmail', 'ns', 'dns',
        'api', 'cdn', 'ftp', 'sftp', 'admin', 'panel', 
        'dashboard', 'control', 'dev', 'test', 'staging', 
        'demo', 'blog', 'forum', 'wiki', 'docs', 'tv',
        'app', 'mobile', 'static', 'assets'
    ]);

    // 加载已注册的域名数据
    loadRegisteredDomains();

    // 输入验证
    subdomainInput.addEventListener('input', function() {
        const value = this.value.toLowerCase();
        const isValid = validateSubdomain(value);
        const inputGroup = this.parentElement;
        const validationHint = inputGroup.nextElementSibling;

        if (value === '') {
            inputGroup.classList.remove('invalid');
            if (validationHint && validationHint.classList.contains('validation-hint')) {
                validationHint.remove();
            }
            return;
        }

        if (isValid) {
            inputGroup.classList.remove('invalid');
            if (validationHint && validationHint.classList.contains('validation-hint')) {
                validationHint.remove();
            }
        } else {
            inputGroup.classList.add('invalid');
            if (!validationHint || !validationHint.classList.contains('validation-hint')) {
                const hint = document.createElement('div');
                hint.className = 'validation-hint error';
                hint.textContent = getValidationMessage(value);
                inputGroup.parentElement.insertBefore(hint, inputGroup.nextSibling);
            }
        }

        checkButton.disabled = !isValid || value === '';
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
        if (!validateSubdomain(subdomain)) return;

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
            if (registeredDomains.has(subdomain)) {
                showResult('unavailable', '域名不可用', `"${subdomain}" 已被其他用户注册`, '已注册');
                return;
            }

            // 域名可用
            showResult('available', '域名可用！', `"${subdomain}.ciao.su" 可以申请`, '');

        } catch (error) {
            console.error('检测失败:', error);
            showResult('error', '检测失败', '无法连接到服务器，请稍后重试', '网络错误');
        } finally {
            // 恢复按钮状态
            setTimeout(() => {
                checkButton.disabled = false;
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
            error: '⚠️'
        };
        resultIcon.textContent = icons[type];

        // 设置文本
        resultText.innerHTML = `
            <h4>${title}</h4>
            <p>${message}</p>
        `;

        // 设置详情
        resultDetails.textContent = details;

        // 设置样式类
        checkerResult.className = `checker-result show ${type}`;
    }

    // 加载已注册的域名数据
    async function loadRegisteredDomains() {
        try {
            const response = await fetch('https://api.github.com/repos/bestzwei/LibreDomains/contents/domains/ciao.su');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const files = await response.json();
            const domainFiles = files.filter(file => 
                file.name.endsWith('.json') && 
                file.name !== 'example.json' &&
                file.type === 'file'
            );

            // 提取域名列表
            registeredDomains.clear();
            const recentDomains = [];

            for (const file of domainFiles) {
                const domainName = file.name.replace('.json', '');
                registeredDomains.add(domainName);
                
                // 获取文件详情用于显示最近注册的域名
                recentDomains.push({
                    name: domainName,
                    url: file.html_url,
                    lastModified: file.name // 简化处理，实际可以通过commit信息获取时间
                });
            }

            // 更新统计信息
            totalDomainsSpan.textContent = registeredDomains.size;

            // 显示最近注册的域名（最多显示12个）
            displayRecentDomains(recentDomains.slice(0, 12));

        } catch (error) {
            console.error('加载域名数据失败:', error);
            recentDomainsList.innerHTML = `
                <div class="error-message">
                    无法加载域名数据，请稍后重试
                </div>
            `;
        }
    }

    // 显示最近注册的域名
    function displayRecentDomains(domains) {
        if (domains.length === 0) {
            recentDomainsList.innerHTML = '<div class="loading">暂无数据</div>';
            return;
        }

        recentDomainsList.innerHTML = domains.map(domain => `
            <div class="domain-item">
                <span class="domain-name">${domain.name}</span>
                <div class="domain-status"></div>
            </div>
        `).join('');

        // 添加点击效果
        const domainItems = recentDomainsList.querySelectorAll('.domain-item');
        domainItems.forEach(item => {
            item.addEventListener('click', () => {
                const domainName = item.querySelector('.domain-name').textContent;
                subdomainInput.value = domainName;
                subdomainInput.focus();
                // 触发检测
                setTimeout(() => {
                    if (!checkButton.disabled) {
                        checkSubdomain();
                    }
                }, 100);
            });
        });
    }

    // 定期刷新数据（每5分钟）
    setInterval(loadRegisteredDomains, 5 * 60 * 1000);
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
