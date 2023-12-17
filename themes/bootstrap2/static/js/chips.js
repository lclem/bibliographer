const allChips = document.querySelectorAll(".chips");
// console.log(allChips);

export function initialiseChips(callback) {
    const observerConfig = {attributes: true, childList: true, subtree: true};
    const observer = new MutationObserver(callback);

    allChips.forEach(chips => {
        // console.log(chips);
        observer.observe(chips, observerConfig);
    });
}

function chipClickHandler(event){
    const target = event.currentTarget;
    const parent = target.parentNode;
    parent.removeChild(target);
}

function addKeyword(target, keyword) {
    console.log(target);
    const divSibling = target.nextElementSibling;
    divSibling.appendChild((() => {
        var _chip = document.createElement('div');

        _chip.classList.add('chip');
        _chip.addEventListener('click', chipClickHandler);

        _chip.append(
            (() => {
                var _chip_text = document.createElement('span');
                _chip_text.classList.add('chip--text');
                _chip_text.innerHTML = keyword;

                return _chip_text;
            })(),
            (() => {
                var _chip_button = document.createElement('span');
                _chip_button.classList.add('chip--button');
                _chip_button.innerHTML = '<strong>x</strong>';

                return _chip_button;
            })()
        );

        return _chip;
    })());
}

export function addChipListener(element) {
    element.addEventListener('keypress', event => {
        const target = event.target;
        const value = target.value;
        if(event.which === 13 && value !== "") {
            event.preventDefault();
            addKeyword(target, value);
            target.value = '';
        }
    });

};

export function chips2string(element) {
    const chips = Array.from(element.parentElement.querySelectorAll(".chip--text").values());
    return chips.map(chip => {
        return chip.textContent;
    }).join(" and ");
}