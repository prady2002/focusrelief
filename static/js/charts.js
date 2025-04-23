// Load analytics data and render charts
function loadAnalyticsData(days = 7) {
    console.log(`Loading analytics data for ${days} days`);
    $.ajax({
        url: `/get_analytics?days=${days}`,
        type: 'GET',
        success: function(data) {
            console.log("Analytics data received:", data);
            renderChart(data);
        },
        error: function(xhr, status, error) {
            console.error("Error loading analytics:", error);
            // Render empty chart to avoid errors
            renderChart({
                daily: [],
                hourly: [],
                totals: {
                    total_screen_time: 0,
                    total_blinks: 0,
                    avg_distance: 0,
                    avg_posture: 0,
                    total_exercises: 0
                }
            });
        }
    });
}

// Render analytics chart
function renderChart(data) {
    const ctx = document.getElementById('analyticsChart');
    if (!ctx) {
        console.error("Analytics chart canvas not found");
        return;
    }
    
    const context = ctx.getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.analyticsChart) {
        window.analyticsChart.destroy();
    }
    
    // Check if we have data
    if (!data.daily || data.daily.length === 0) {
        // Create empty chart with message
        window.analyticsChart = new Chart(context, {
            type: 'bar',
            data: {
                labels: ['No Data'],
                datasets: [{
                    label: 'No data available',
                    data: [0],
                    backgroundColor: 'rgba(200, 200, 200, 0.5)'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'No analytics data available yet'
                    }
                }
            }
        });
        return;
    }
    
    // Prepare data
    const labels = data.daily.map(day => day.date);
    const screenTimeData = data.daily.map(day => day.screen_time_minutes / 60); // Convert to hours
    const blinkData = data.daily.map(day => day.blink_count);
    
    // Create chart
    window.analyticsChart = new Chart(context, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Screen Time (hours)',
                    data: screenTimeData,
                    backgroundColor: 'rgba(67, 97, 238, 0.7)',
                    borderColor: 'rgba(67, 97, 238, 1)',
                    borderWidth: 1,
                    yAxisID: 'y'
                },
                {
                    label: 'Blink Count',
                    data: blinkData,
                    backgroundColor: 'rgba(76, 175, 80, 0.7)',
                    borderColor: 'rgba(76, 175, 80, 1)',
                    borderWidth: 1,
                    type: 'line',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Screen Time (hours)'
                    },
                    min: 0
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false
                    },
                    title: {
                        display: true,
                        text: 'Blink Count'
                    },
                    min: 0
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Screen Time & Blink Analysis'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.datasetIndex === 0) {
                                label += context.parsed.y.toFixed(2) + ' hours';
                            } else {
                                label += context.parsed.y + ' blinks';
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
    
    console.log("Chart rendered successfully");
}

// Call loadAnalyticsData when page loads
$(document).ready(function() {
    console.log("Charts script loaded");
    // loadAnalyticsData will be called from main.js
});
