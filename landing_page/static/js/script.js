document.addEventListener('DOMContentLoaded', function() {
<<<<<<< HEAD
=======
    console.log('DOM loaded');
    
>>>>>>> 3c1b82c32efc8d5ab0d855a36c6c86fc3a730fba
    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
<<<<<<< HEAD
    menuToggle.addEventListener('click', function() {
        navLinks.classList.toggle('active');
        menuToggle.classList.toggle('active');
    });
=======
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });
    }
>>>>>>> 3c1b82c32efc8d5ab0d855a36c6c86fc3a730fba
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
<<<<<<< HEAD
                navLinks.classList.remove('active');
                menuToggle.classList.remove('active');
=======
                if (navLinks) {
                    navLinks.classList.remove('active');
                    menuToggle.classList.remove('active');
                }
>>>>>>> 3c1b82c32efc8d5ab0d855a36c6c86fc3a730fba
            }
        });
    });
    
    // Typewriter effect for subtitle
    const subtitle = document.querySelector('.subtitle');
    if (subtitle) {
        const text = subtitle.textContent;
        subtitle.textContent = '';
        
        let i = 0;
        const typingEffect = setInterval(() => {
            if (i < text.length) {
                subtitle.textContent += text.charAt(i);
                i++;
            } else {
                clearInterval(typingEffect);
            }
        }, 50);
    }
    
    // Animate cards when they come into view
    const animateOnScroll = () => {
        const cards = document.querySelectorAll('.feature-card, .step-card, .team-member');
        
        cards.forEach(card => {
            const cardPosition = card.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.3;
            
            if (cardPosition < screenPosition) {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }
        });
    };
    
    // Set initial state for animation
    const cards = document.querySelectorAll('.feature-card, .step-card, .team-member');
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.6s ease';
    });
    
    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll(); // Run once on load
<<<<<<< HEAD
=======
    
    // ============================================
    // CHART.JS CONFIGURATIONS - FIXED VERSION
    // ============================================
    
    // Wait a bit to ensure Chart.js is fully loaded
    setTimeout(() => {
        console.log('Checking Chart.js...');
        
        // Check if Chart.js is loaded
        if (typeof Chart === 'undefined') {
            console.error('Chart.js not loaded');
            return;
        }
        
        console.log('Chart.js loaded successfully');
        
        // Chart configurations
        Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";

        // 1. Engagement Chart
        const engagementCtx = document.getElementById('engagementChart');
        if (engagementCtx) {
            console.log('Creating engagement chart');
            try {
                new Chart(engagementCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Don\'t Pay Attention', 'Daydream', 'Feel Overwhelmed', 'Doze Off', 'Engaged'],
                        datasets: [{
                            data: [75, 91, 45, 39, 25],
                            backgroundColor: [
                                '#ff6b6b',
                                '#ee5a24',
                                '#feca57',
                                '#ff9ff3',
                                '#54a0ff'
                            ],
                            borderWidth: 3,
                            borderColor: '#fff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    padding: 8,
                                    usePointStyle: true,
                                    font: {
                                        size: 10
                                    }
                                }
                            }
                        }
                    }
                });
                console.log('Engagement chart created');
            } catch (error) {
                console.error('Error creating engagement chart:', error);
            }
        } else {
            console.log('Engagement chart canvas not found');
        }

        // 2. Attention Span Chart
        const attentionCtx = document.getElementById('attentionChart');
        if (attentionCtx) {
            console.log('Creating attention chart');
            try {
                new Chart(attentionCtx, {
                    type: 'line',
                    data: {
                        labels: ['0-15 min', '15-30 min', '30-45 min', '45-50 min', '50+ min'],
                        datasets: [{
                            label: 'Attention Rate (%)',
                            data: [91, 48, 64, 36, 4],
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            fill: true,
                            tension: 0.4,
                            borderWidth: 3,
                            pointBackgroundColor: '#667eea',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 3,
                            pointRadius: 8
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100,
                                ticks: {
                                    callback: function(value) {
                                        return value + '%';
                                    }
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
                console.log('Attention chart created');
            } catch (error) {
                console.error('Error creating attention chart:', error);
            }
        }

        // 3. Distractions Chart
        const distractionsCtx = document.getElementById('distractionsChart');
        if (distractionsCtx) {
            console.log('Creating distractions chart');
            try {
                new Chart(distractionsCtx, {
                    type: 'bar',
                    data: {
                        labels: ['Email/Messages', 'Unrelated Work', 'House Chores', 'Social Media', 'Other Activities'],
                        datasets: [{
                            label: 'Percentage of Employees',
                            data: [55, 49, 15, 75, 92],
                            backgroundColor: [
                                '#3742fa',
                                '#2f3542',
                                '#ff4757',
                                '#5352ed',
                                '#70a1ff'
                            ],
                            borderRadius: 6,
                            borderSkipped: false
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100,
                                ticks: {
                                    callback: function(value) {
                                        return value + '%';
                                    }
                                }
                            }
                        }
                    }
                });
                console.log('Distractions chart created');
            } catch (error) {
                console.error('Error creating distractions chart:', error);
            }
        }

        // 4. Structure Chart
        const structureCtx = document.getElementById('structureChart');
        if (structureCtx) {
            console.log('Creating structure chart');
            try {
                new Chart(structureCtx, {
                    type: 'polarArea',
                    data: {
                        labels: ['No Agenda (Recurring)', 'No Agenda (One-off)', 'Brief Agendas', 'Missed Meetings', 'Structured Meetings'],
                        datasets: [{
                            data: [64, 60, 21, 96, 37],
                            backgroundColor: [
                                '#ff6b6b',
                                '#ee5a24',
                                '#feca57',
                                '#ff9ff3',
                                '#54a0ff'
                            ],
                            borderColor: '#fff',
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    padding: 8,
                                    usePointStyle: true,
                                    font: {
                                        size: 9
                                    }
                                }
                            }
                        },
                        scales: {
                            r: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                });
                console.log('Structure chart created');
            } catch (error) {
                console.error('Error creating structure chart:', error);
            }
        }

        // 5. Environment Chart
        const environmentCtx = document.getElementById('environmentChart');
        if (environmentCtx) {
            console.log('Creating environment chart');
            try {
                new Chart(environmentCtx, {
                    type: 'radar',
                    data: {
                        labels: ['From Bed', 'While Walking', 'Public Transport', 'Home Office', 'Traditional Office'],
                        datasets: [{
                            label: 'Percentage of Users',
                            data: [42, 21, 11, 65, 35],
                            borderColor: '#764ba2',
                            backgroundColor: 'rgba(118, 75, 162, 0.2)',
                            borderWidth: 3,
                            pointBackgroundColor: '#764ba2',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2,
                            pointRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            r: {
                                beginAtZero: true,
                                max: 70,
                                ticks: {
                                    stepSize: 10
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
                console.log('Environment chart created');
            } catch (error) {
                console.error('Error creating environment chart:', error);
            }
        }

        // 6. Video Benefits Chart
        const videoCtx = document.getElementById('videoChart');
        if (videoCtx) {
            console.log('Creating video chart');
            try {
                new Chart(videoCtx, {
                    type: 'bar',
                    data: {
                        labels: ['Feel More Connected', 'Better Discussion Quality', 'Cannot Multitask (Camera On)', 'Better Productivity'],
                        datasets: [{
                            label: 'Positive Impact (%)',
                            data: [75, 75, 66, 43],
                            backgroundColor: [
                                '#26de81',
                                '#2bcbba',
                                '#45aaf2',
                                '#a55eea'
                            ],
                            borderRadius: 8,
                            borderSkipped: false
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        indexAxis: 'y',
                        plugins: {
                            legend: {
                                display: false
                            }
                        },
                        scales: {
                            x: {
                                beginAtZero: true,
                                max: 100,
                                ticks: {
                                    callback: function(value) {
                                        return value + '%';
                                    }
                                }
                            }
                        }
                    }
                });
                console.log('Video chart created');
            } catch (error) {
                console.error('Error creating video chart:', error);
            }
        }
        
    }, 1000); // Wait 1 second for Chart.js to load
>>>>>>> 3c1b82c32efc8d5ab0d855a36c6c86fc3a730fba
});