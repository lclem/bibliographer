import {statusAppend, getXmlHttp} from 'https://lclem.github.io/librarian/theme/js/util.js';

// given a url fetch its contents and invoke the callback function on the result
export async function getWebPageAdvanced(theUrl, doneCallback, callback) {

    var xmlhttp = getXmlHttp();

    xmlhttp.onreadystatechange = async e => {
        // console.log(e);
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            let res = xmlhttp.responseText;
            // console.log("res: " + res);
            doneCallback(res);
        }
        else {
            // statusAppend("status: " + xmlhttp.status);
        }
    }

    try {
        xmlhttp.open("GET", theUrl, true);
        xmlhttp.onabort = callback;
        xmlhttp.onerror = callback;
        xmlhttp.onload = callback;
        xmlhttp.onloadend = callback;
        xmlhttp.onloadstart = callback;
        xmlhttp.onprogress = callback;
        xmlhttp.ontimeout = callback;
        xmlhttp.send();
    } catch (err) {
        statusAppend('GET error: ', err);
    }

}

export async function loadTextArray(fileName, callback, progressBar = null) {
    getWebPageAdvanced(fileName, async text => {
        const entries = text.split("\n");
        statusAppend(`loaded ${entries.length} entries from ${fileName}`);
        callback(entries);
    }, async event => {
        console.log(event);
        if (progressBar == null) {
            console.log('progress bar is null, ignoring');
            return;
        }
        else if (event.type == "load") {
            progressBar.style.width = "0%";
            progressBar.style.opacity = 100;
        }
        else if (event.type == "loadend") {
            progressBar.style.opacity = 0;
            progressBar.style.width = "100%";
        }
        else if (event.type == "progress") {
            progressBar.style.opacity = 100;
            if (event.lengthComputable) {
                const percentComplete = event.loaded / event.total * 100;
                progressBar.style.width = `${percentComplete}%`;
                // console.log(percentComplete);
            } else if (event.loaded)
                // we only know the received amount and not the total amount
                console.log('downloaded:', event.loaded);
        }
    });
}

// Create a new 'change' event
export const changeEvent = new Event('change');
export const keyDownEvent = new Event('keydown');
export const keyEnterEvent = new KeyboardEvent('keypress',  {keyCode : 13});

export function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}