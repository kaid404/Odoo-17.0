document.addEventListener("DOMContentLoaded", () => {
  const themeToggleBtn = document.getElementById("theme-toggle");
  const currentTheme = localStorage.getItem("theme") || "light-theme";
  document.body.className = currentTheme;

  themeToggleBtn.addEventListener("click", () => {
    if (document.body.classList.contains("light-theme")) {
      document.body.className = "dark-theme";
      localStorage.setItem("theme", "dark-theme");
    } else {
      document.body.className = "light-theme";
      localStorage.setItem("theme", "light-theme");
    }
  });
if (document.querySelector('.edit-profile-btn')) {
document.querySelector('.edit-profile-btn').addEventListener('click', function() {
    alert('Edit profile feature is under development!');
});
}


});

let menuicn = document.querySelector(".menuicn");
let nav = document.querySelector(".navcontainer");
menuicn.addEventListener("click", () => {
  nav.classList.toggle("navclose");
});

function toggleFullscreen() {
    const elem = document.documentElement;
    const icon = document.getElementById("fullscreen-toggle");

    if (!document.fullscreenElement) {
        elem.requestFullscreen().then(() => {
            icon.classList.remove("fa-expand");
            icon.classList.add("fa-compress");
        }).catch((err) => {
            alert(`Error attempting to enable full-screen mode: ${err.message}`);
        });
    } else {
        document.exitFullscreen().then(() => {
            icon.classList.remove("fa-compress");
            icon.classList.add("fa-expand");
        }).catch((err) => {
            alert(`Error attempting to exit full-screen mode: ${err.message}`);
        });
    }
}


//
//$(document).ready(function () {
//    // Define the fetchSubjects function inside the document ready function
//    function fetchSubjects(class_id) {
//        if (class_id) {
//            $.ajax({
//                url: '/get_subjects_by_class',
//                type: 'POST',
//                data: JSON.stringify({'class_id': class_id}),
//                contentType: 'application/json',
//                success: function (response) {
//                    $('#subject_table').empty();
//                    response.subjects.forEach(function (subject) {
//                        $('#subject_table').append(
//                            '<tr>' +
//                                '<td>' + subject.name + '</td>' +
//                                '<td>' + subject.description + '</td>' +
//                            '</tr>'
//                        );
//                    });
//                },
//                error: function () {
//                    alert('Failed to fetch subjects.');
//                }
//            });
//        }
//    }
//
//    // Assign onchange event handler to your select element
//    $('#class_select').on('change', function () {
//        const selectedClassId = $(this).val(); // Get selected class id
//        fetchSubjects(selectedClassId); // Call the fetchSubjects function
//    });
//});
