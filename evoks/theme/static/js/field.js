function createInput(value, id) {
    return `
    <div class="flex-grow mt-2 col-span-2">
    <textarea type="text" name="new-obj" id="${id}" maxlength=5000
        class="shadow-sm w-full focus:ring-gray-500 focus:border-gray-500 block sm:text-sm border-gray-300 rounded-md"
        >${value}</textarea>
    </div>`.trim()
}


function changeToInput(id) {
    const button = document.getElementById(id)
    const { inner, outer } = button.dataset
    const valueId = `title-value-${outer}-${inner}`
    const languageDisplay = document.getElementById(`title-language-${outer}-${inner}`)
    const languageEditor = document.getElementById(`title-language-editor-${outer}-${inner}`)
    const languageSelect = document.getElementById(`title-language-select-${outer}-${inner}`)

    const value = document.getElementById(valueId)

    if (button.innerText === 'Save') {
        button.innerText = 'Update'
        button.type = 'submit'
        value.innerHTML = document.getElementById(`title-value-input-${outer}-${inner}`).value
        if (languageSelect) {
            languageSelect.disabled = false
        }
    } else {
        button.innerText = 'Save'
        const inputValue = document.createElement('template')
        inputValue.innerHTML = createInput(value.innerText, `title-value-input-${outer}-${inner}`)
        value.parentElement.replaceChild(inputValue.content.firstChild, value)
        if (languageSelect) {
            languageSelect.disabled = false
            languageEditor.classList.remove('hidden')
            languageEditor.classList.add('flex')
            languageDisplay.style.display = 'none'
        }
    }

}