
document.getElementById("create-tag-button").addEventListener("click", function(e) {
    document.getElementById("create-tag-modal").classList.toggle("invisible");
});

document.getElementById("create-property-button").addEventListener("click", function(e) {
    document.getElementById("create-property-modal").classList.toggle("invisible");
});
// broader option 2
document.getElementById("create-broader-button").addEventListener("click", function(e) {
    document.getElementById("create-broader-modal").classList.toggle("invisible");
});
document.getElementById("delete-term-button").addEventListener("click", function(e) {
    document.getElementById("delete-term-modal").classList.toggle("invisible");
});
