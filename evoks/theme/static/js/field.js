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

    const value = document.getElementById(valueId)


    if (button.innerText === 'Save') {
        button.innerText = 'Update'
        button.type = 'submit'
        value.innerHTML = document.getElementById(`title-value-input-${outer}-${inner}`).value
    } else {
        button.innerText = 'Save'
        const inputValue = document.createElement('template')
        inputValue.innerHTML = createInput(value.innerText, `title-value-input-${outer}-${inner}`)
        value.parentElement.replaceChild(inputValue.content.firstChild, value)
    }

}