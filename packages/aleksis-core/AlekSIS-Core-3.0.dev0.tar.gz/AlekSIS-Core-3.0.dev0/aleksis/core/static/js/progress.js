const OPTIONS = getJSONScript("progress_options");

const STYLE_CLASSES = {
    10: 'info',
    20: 'info',
    25: 'success',
    30: 'warning',
    40: 'error',
};

const ICONS = {
    10: 'mdi:information',
    20: 'mdi:information',
    25: 'mdi:check-circle',
    30: 'mdi:alert-outline',
    40: 'mdi:alert-octagon-outline',
};

function setProgress(progress) {
    $("#progress-bar").css("width", progress + "%");
}

function renderMessageBox(level, text) {
    return '<div class="alert ' + STYLE_CLASSES[level] + '"><p><i class="material-icons iconify left" data-icon="' + ICONS[level] + '"></i>' + text + '</p></div>';
}

function updateMessages(messages) {
    const messagesBox = $("#messages");

    // Clear container
    messagesBox.html("");

    // Render message boxes
    $.each(messages, function (i, message) {
        messagesBox.append(renderMessageBox(message[0], message[1]));
    });
}

function customProgress(progressBarElement, progressBarMessageElement, progress) {
    setProgress(progress.percent);

    if (progress.hasOwnProperty("messages")) {
        updateMessages(progress.messages);
    }
}


function customSuccess(progressBarElement, progressBarMessageElement, result) {
    setProgress(100);
    if (result) {
        updateMessages(result);
    }
    $("#result-alert").addClass("success");
    $("#result-icon").attr("data-icon", "mdi:check-circle-outline");
    $("#result-text").text(OPTIONS.success);
    $("#result-box").show();
    $("#result-button").show();
    const redirect = "redirect_on_success" in OPTIONS && OPTIONS.redirect_on_success;
    if (redirect) {
        window.location.replace(OPTIONS.redirect_on_success);
    }
}

function customError(progressBarElement, progressBarMessageElement, excMessage) {
    setProgress(100);
    if (excMessage) {
        updateMessages([40, excMessage]);
    }
    $("#result-alert").addClass("error");
    $("#result-icon").attr("data-icon", "mdi:alert-octagon-outline");
    $("#result-text").text(OPTIONS.error);
    $("#result-box").show();
}

$(document).ready(function () {
    $("#progress-bar").removeClass("indeterminate").addClass("determinate");

    var progressUrl = Urls["taskStatus"](OPTIONS.task_id);
    CeleryProgressBar.initProgressBar(progressUrl, {
        onProgress: customProgress,
        onSuccess: customSuccess,
        onError: customError,
    });
});
