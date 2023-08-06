const handleClick = (el) => {
    const keyPress = { 'key': el.target.value };
    const options = {
        'method': 'POST',
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': JSON.stringify(keyPress),
    };
    fetch('/', options)
        .then(r => console.log(r))
        .catch(e => console.error(e));
}

document.querySelectorAll('.key').forEach(e => e.addEventListener('click', handleClick))
