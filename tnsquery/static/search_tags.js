const input_text = document.getElementById('iauname');
var tags_div = document.getElementById('search_tags');

input_text.addEventListener('keyup', function(event){

    if(event.key.value != 13){
        create_tags(event.target.value)
    }
});

function create_tags(word) {
    const tags = word.split(',').filter(tag => tag.trim() !== '').map(tag => tag.trim())
    tags_div.innerHTML = ''
    tags.forEach(tag => {
        // const table_col = document.createElement('td');
        const kbd_element = document.createElement('kbd');
        kbd_element.innerText = tag
        // table_col.appendChild(kbd_element)
        tags_div.appendChild(kbd_element)
        tags_div.appendChild( document.createTextNode( '\u00A0' ) );
    })
}