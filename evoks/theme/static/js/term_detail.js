
function createInput(value, id) {
    return `
    <div class="flex-shrink-0 flex-grow">
    <input type="text" name="name" id="${id}" value="${value}"
        class="shadow-sm focus:ring-gray-500 focus:border-gray-500 block w-3/4 sm:text-sm border-gray-300 rounded-md"
        >
    </div>`.trim()
}

document.getElementById("create-tag-button").addEventListener("click", function(e) {
    document.getElementById("create-tag-modal").classList.toggle("invisible");
});

document.getElementById("create-property-button").addEventListener("click", function(e) {
    document.getElementById("create-property-modal").classList.toggle("invisible");
});

document.getElementById("delete-term-button").addEventListener("click", function(e) {
    document.getElementById("delete-term-modal").classList.toggle("invisible");
});

document.getElementById('title-update-button').addEventListener('click', function(e) {

    const button = document.getElementById('title-update-button')
    const value = document.getElementById('title-value')

    const title = document.getElementById('title-subject')

    if (button.innerText === 'Save') {
        button.innerText = 'Update' 
        title.innerHTML = document.getElementById('title-subject-input').value
        value.innerHTML = document.getElementById('title-value-input').value
    } else {
        button.innerText = 'Save'
        const inputValue = document.createElement('template')
        inputValue.innerHTML = createInput(value.innerText, 'title-value-input')
        value.replaceChildren(inputValue.content.firstChild)
    
        const inputSubject = document.createElement('template')
        inputSubject.innerHTML = createInput(title.innerText, 'title-subject-input')
        title.replaceChildren(inputSubject.content.firstChild)
    }
});