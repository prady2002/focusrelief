// Define eye exercises
const eyeExercises = [
    {
        name: "Focus Change",
        instructions: "Hold your finger a few inches from your eye. Focus on it. Slowly move your finger away. Focus far away, then back on your finger.",
        duration: 15
    },
    {
        name: "20-20-20 Exercise",
        instructions: "Look at something at least 20 feet away for 20 seconds. This reduces eye strain from focusing near objects.",
        duration: 20
    },
    {
        name: "Eye Rolling",
        instructions: "Roll your eyes in a clockwise direction for 5 seconds, then counterclockwise for 5 seconds. Repeat.",
        duration: 15
    },
    {
        name: "Palming",
        instructions: "Rub your hands together until warm. Place them over your closed eyes for 10 seconds without pressing on the eyes.",
        duration: 10
    }
];

let currentExerciseIndex = 0;
let exerciseInterval;
let totalExerciseTime = 60; // 1 minute total
let timeRemaining = 0;

function startExerciseRoutine() {
    currentExerciseIndex = 0;
    timeRemaining = totalExerciseTime;
    showCurrentExercise();
    
    // Update the exercise timer every second
    exerciseInterval = setInterval(updateExerciseTimer, 1000);
}

function stopExerciseRoutine() {
    clearInterval(exerciseInterval);
}

function showCurrentExercise() {
    // Calculate which exercise to show based on time elapsed
    let timeElapsed = totalExerciseTime - timeRemaining;
    let cumulativeTime = 0;
    
    for (let i = 0; i < eyeExercises.length; i++) {
        cumulativeTime += eyeExercises[i].duration;
        if (timeElapsed < cumulativeTime) {
            currentExerciseIndex = i;
            break;
        }
    }
    
    const exercise = eyeExercises[currentExerciseIndex];
    $('#exercise-name').text(exercise.name);
    $('#exercise-instructions').text(exercise.instructions);
    
    // Calculate progress for this specific exercise
    const exerciseElapsed = timeElapsed - (cumulativeTime - exercise.duration);
    const exerciseProgress = (exerciseElapsed / exercise.duration) * 100;
    
    // Update progress bar
    $('#exercise-progress').css('width', `${exerciseProgress}%`);
}

function updateExerciseTimer() {
    if (timeRemaining <= 0) {
        clearInterval(exerciseInterval);
        $('#exercise-container').addClass('d-none');
        $('#start-exercise').removeClass('d-none');
        
        // Notify the server that exercise is complete
        $.ajax({
            url: '/stop_exercise',
            type: 'GET'
        });
        
        return;
    }
    
    timeRemaining--;
    $('#exercise-timer').text(`${timeRemaining}s`);
    
    // Update overall progress
    const progress = ((totalExerciseTime - timeRemaining) / totalExerciseTime) * 100;
    $('#exercise-progress').css('width', `${progress}%`);
    
    // Check if we need to switch to next exercise
    showCurrentExercise();
    
    // Check with the server if the exercise is still active
    $.ajax({
        url: '/get_exercise_time',
        type: 'GET',
        success: function(data) {
            if (!data.active) {
                clearInterval(exerciseInterval);
                $('#exercise-container').addClass('d-none');
                $('#start-exercise').removeClass('d-none');
            }
        }
    });
}
