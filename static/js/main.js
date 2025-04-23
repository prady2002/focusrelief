$(document).ready(function() {
    // Update screen time
    function updateTimer() {
        $.ajax({
            url: '/get_screen_time',
            type: 'GET',
            success: function(data) {
                const minutes = String(data.minutes).padStart(2, '0');
                const seconds = String(data.seconds).padStart(2, '0');
                $('#timer').text(`${minutes}:${seconds}`);
            },
            error: function() {
                $('#connection-status').removeClass('bg-success').addClass('bg-danger').text('Disconnected');
            }
        });
    }
    
    // Update break timer if active
    // Break Timer functionality
let alarmPlaying = false;

// Update break timer if active
function updateBreakTimer() {
    $.ajax({
        url: '/get_break_time',
        type: 'GET',
        success: function(data) {
            if (data.active) {
                $('#break-timer-display').removeClass('d-none');
                const minutes = String(data.minutes).padStart(2, '0');
                const seconds = String(data.seconds).padStart(2, '0');
                $('#break-timer-countdown').text(`${minutes}:${seconds}`);
                
                // Check if timer finished
                if (data.is_finished || (data.minutes === 0 && data.seconds === 0)) {
                    if (!alarmPlaying) {
                        playAlarm();
                    }
                }
            } else {
                $('#break-timer-display').addClass('d-none');
                stopAlarm();
            }
        }
    });
}

// Set custom break timer
$('#set-break-timer').click(function() {
    const minutes = $('#break-minutes').val();
    if (minutes > 0) {
        $.ajax({
            url: '/set_custom_break',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                minutes: parseInt(minutes)
            }),
            success: function(response) {
                $('#break-timer-display').removeClass('d-none');
                console.log("Break timer set successfully:", response);
            },
            error: function(xhr, status, error) {
                console.error("Error setting break timer:", error);
            }
        });
    }
});

// Cancel custom break timer
$('#cancel-break').click(function() {
    $.ajax({
        url: '/cancel_custom_break',
        type: 'GET',
        success: function() {
            $('#break-timer-display').addClass('d-none');
            stopAlarm();
        }
    });
});

// Play alarm sound
function playAlarm() {
    alarmPlaying = true;
    const alarmSound = document.getElementById('alarm-sound');
    alarmSound.loop = true;
    alarmSound.play().catch(error => {
        console.error("Error playing alarm:", error);
    });
    
    // Show alert notification
    if ("Notification" in window && Notification.permission === "granted") {
        new Notification("Break Time!", {
            body: "Your scheduled break time has arrived!",
            icon: "/static/images/clock.png" // Add a clock icon if available
        });
    } else if ("Notification" in window && Notification.permission !== "denied") {
        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                new Notification("Break Time!", {
                    body: "Your scheduled break time has arrived!",
                    icon: "/static/images/clock.png"
                });
            }
        });
    }
    
    // Add visual indication that alarm is active
    $('#break-timer-countdown').addClass('text-danger fw-bold');
}

// Stop alarm sound
function stopAlarm() {
    alarmPlaying = false;
    const alarmSound = document.getElementById('alarm-sound');
    alarmSound.pause();
    alarmSound.currentTime = 0;
    $('#break-timer-countdown').removeClass('text-danger fw-bold');
}

// Add a button to stop the alarm
$('#break-timer-display').append('<button id="stop-alarm" class="btn btn-sm btn-warning ms-2">Stop Alarm</button>');

// Handle stop alarm button
$('#stop-alarm').click(function() {
    stopAlarm();
});

// Request notification permission on page load
$(document).ready(function() {
    if ("Notification" in window && Notification.permission !== "granted") {
        Notification.requestPermission();
    }
});

    
    // Initialize timers
    setInterval(updateTimer, 1000);
    setInterval(updateBreakTimer, 1000);
    
    // Reset screen time timer
    $('#resetTimer').click(function() {
        $.ajax({
            url: '/reset_timer',
            type: 'GET',
            success: function() {
                $('#timer').text('00:00');
            }
        });
    });
    
    // Toggle settings
    $('#blinkReminder').change(function() {
        const isEnabled = $(this).prop('checked');
        $.ajax({
            url: `/toggle_setting/blink_reminder_enabled/${isEnabled}`,
            type: 'GET'
        });
    });
    
    $('#screenTimeReminder').change(function() {
        const isEnabled = $(this).prop('checked');
        $.ajax({
            url: `/toggle_setting/screen_time_reminder_enabled/${isEnabled}`,
            type: 'GET'
        });
    });
    
    $('#distanceReminder').change(function() {
        const isEnabled = $(this).prop('checked');
        $.ajax({
            url: `/toggle_setting/distance_reminder_enabled/${isEnabled}`,
            type: 'GET'
        });
    });
    
    $('#customBreakEnabled').change(function() {
        const isEnabled = $(this).prop('checked');
        $.ajax({
            url: `/toggle_setting/custom_break_enabled/${isEnabled}`,
            type: 'GET'
        });
    });
    
    // Handle sliders
    $('#blinkReminderTime').on('input', function() {
        const value = $(this).val();
        $('#blinkTimeValue').text(value);
    });
    
    $('#blinkReminderTime').change(function() {
        const value = $(this).val();
        $.ajax({
            url: '/update_setting',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                setting: 'blink_reminder_time',
                value: value
            })
        });
    });
    
    $('#screenTimeInterval').on('input', function() {
        const value = $(this).val();
        $('#screenTimeValue').text(value);
    });
    
    $('#screenTimeInterval').change(function() {
        const value = $(this).val();
        $.ajax({
            url: '/update_setting',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                setting: 'screen_time_interval',
                value: value
            })
        });
    });
    
    $('#minDistance').on('input', function() {
        const value = $(this).val();
        $('#distanceValue').text(value);
    });
    
    $('#minDistance').change(function() {
        const value = $(this).val();
        $.ajax({
            url: '/update_setting',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                setting: 'min_distance',
                value: value
            })
        });
    });
    
    $('#customBreakInterval').on('input', function() {
        const value = $(this).val();
        $('#customBreakValue').text(value);
    });
    
    $('#customBreakInterval').change(function() {
        const value = $(this).val();
        $.ajax({
            url: '/update_setting',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                setting: 'custom_break_interval',
                value: value
            })
        });
        
        // Update the input field value as well
        $('#break-minutes').val(value);
    });
    
    // Set custom break timer
    $('#set-break-timer').click(function() {
        const minutes = $('#break-minutes').val();
        if (minutes > 0) {
            $.ajax({
                url: '/set_custom_break',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    minutes: minutes
                }),
                success: function() {
                    $('#break-timer-display').removeClass('d-none');
                }
            });
        }
    });
    
    // Cancel custom break timer
    $('#cancel-break').click(function() {
        $.ajax({
            url: '/cancel_custom_break',
            type: 'GET',
            success: function() {
                $('#break-timer-display').addClass('d-none');
            }
        });
    });
    
    // Start eye exercise
    $('#start-exercise').click(function() {
        $.ajax({
            url: '/start_exercise',
            type: 'GET',
            success: function() {
                $('#exercise-container').removeClass('d-none');
                $('#start-exercise').addClass('d-none');
                startExerciseRoutine();
            }
        });
    });
    
    // Stop eye exercise
    $('#stop-exercise').click(function() {
        $.ajax({
            url: '/stop_exercise',
            type: 'GET',
            success: function() {
                $('#exercise-container').addClass('d-none');
                $('#start-exercise').removeClass('d-none');
                stopExerciseRoutine();
            }
        });
    });
    
    // Load initial settings
    function loadSettings() {
        $.ajax({
            url: '/get_settings',
            type: 'GET',
            success: function(settings) {
                // Update checkboxes
                $('#blinkReminder').prop('checked', settings.blink_reminder_enabled);
                $('#screenTimeReminder').prop('checked', settings.screen_time_reminder_enabled);
                $('#distanceReminder').prop('checked', settings.distance_reminder_enabled);
                $('#customBreakEnabled').prop('checked', settings.custom_break_enabled);
                
                // Update sliders and values
                $('#blinkReminderTime').val(settings.blink_reminder_time);
                $('#blinkTimeValue').text(settings.blink_reminder_time);
                
                $('#screenTimeInterval').val(settings.screen_time_interval);
                $('#screenTimeValue').text(settings.screen_time_interval);
                
                $('#minDistance').val(settings.min_distance);
                $('#distanceValue').text(settings.min_distance);
                
                $('#customBreakInterval').val(settings.custom_break_interval);
                $('#customBreakValue').text(settings.custom_break_interval);
                $('#break-minutes').val(settings.custom_break_interval);
            }
        });
    }
    
    // Load settings on page load
    loadSettings();
});
