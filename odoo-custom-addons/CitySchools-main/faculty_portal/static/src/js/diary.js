 // Function to fetch subjects related to the selected class
function fetchSubjects(class_id) {

   
    if (class_id) {
        console.log(class_id,'<---class_id')
        fetch('/get_subjects_by_class', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'class_id':class_id
            },
            body: JSON.stringify({'class_id': class_id}),

        })
        .then(response => response.json())
        .then(data => {
            if (data.subjects) {
                const subjectTable = document.getElementById('subject_table').querySelector('tbody');
                subjectTable.innerHTML = '';

                data.subjects.forEach((subject, index) => {
    const row = document.createElement('tr');

    const nameCell = document.createElement('td');
    const nameInput = document.createElement('input');
    nameInput.setAttribute('type', 'hidden');
    nameInput.setAttribute('name', 'subject_name[]');
    nameInput.value = subject.name;
    nameCell.textContent = subject.name;
    nameCell.appendChild(nameInput);

    const classCell = document.createElement('td');
    const classInput = document.createElement('input');
    classInput.setAttribute('type', 'hidden');
    classInput.setAttribute('name', 'class_name[]');
    classInput.value = subject.class_id;
    classCell.textContent = subject.class_id;
    classCell.appendChild(classInput);

//    const dateCell = document.createElement('td');
//    const currentDate = new Date();
//    const formattedDate = currentDate.toISOString().split('T')[0];
//    dateCell.textContent = formattedDate;

    const descriptionCell = document.createElement('td');
    const descriptionInput = document.createElement('input');
    descriptionInput.setAttribute('name', 'description[]');
    descriptionInput.setAttribute('placeholder', 'Enter description here...');
    descriptionInput.classList.add('description_input');
    descriptionCell.appendChild(descriptionInput);

     descriptionInput.addEventListener('input', function () {
        console.log(`Input value for ${descriptionInput.id}:`, descriptionInput.value);
    });


    row.appendChild(nameCell);
    row.appendChild(classCell);
//    row.appendChild(dateCell);
    row.appendChild(descriptionCell);
    subjectTable.appendChild(row);
});

            } else {
                alert('No subjects found for the selected class.');
            }
        })
        .catch(() => {
            alert('Failed to fetch subjects.');
        });
    }
}
