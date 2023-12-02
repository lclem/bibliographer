import { statusAppend, sanitiseKey, lowerize, getWebPage, doi2bib, isDoi, toBase64, storkInit } from 'https://lclem.github.io/librarian/theme/js/util.js';
import { openGitHub, uploadFile } from 'https://lclem.github.io/librarian/theme/js/github.js';

let addButton = document.getElementById('add-button');
var stork_input = document.getElementById('stork-input');
let dropArea = document.getElementById('drop-area');
let status = document.getElementById('status');
let dt = [];
let bibStr = "";

var bibFile;

window.storkInit = storkInit;

stork_input.addEventListener("change", updateSearch, false);
// stork_input.addEventListener("input", updateSearch, false);
stork_input.addEventListener("paste", detectPaste, false);

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {dropArea.addEventListener(eventName, preventDefaults, false)});
['dragenter', 'dragover'].forEach(eventName => {dropArea.addEventListener(eventName, highlight, false)});
['dragleave', 'drop'].forEach(eventName => {dropArea.addEventListener(eventName, unhighlight, false)});
dropArea.addEventListener('drop', handleDrop, false)

const target = document.querySelector("div.target");

function preventDefaults (e) {
  e.preventDefault()
  e.stopPropagation()
}

function highlight(e) {
  dropArea.classList.add('highlight')
}

function unhighlight(e) {
  dropArea.classList.remove('highlight')
}

function handleDrop(e) {
  dt = e.dataTransfer;
  var len = dt.files.length;

  if (len != 1) {
    console.log("not supported: dropped files #" + len);
    return;
  }

  var theFile = dt.files[0];
  var fileName = theFile.name;

  if (fileName.endsWith(".bib") || fileName.endsWith(".txt")) {
    uploadBib(dt);
  }
  else if (fileName.endsWith(".pdf")) {
    uploadPdf(theFile);
  }
  else {
    console.log("unsupported format: " + fileName);
  }
}

const copyBib = async () => {
  try {
    let text = document.getElementById('bib').innerHTML;
    await navigator.clipboard.writeText(text);

    // var tooltip = document.getElementById("myTooltip");
    // tooltip.innerHTML = "copied to clipboard!";
    console.log('Content copied to clipboard');
  } catch (err) {
    // tooltip.innerHTML = "error: "+ err;
    console.error('Failed to copy: ', err);
  }
}

function triggerStorkSearch(str) {
  console.log('triggerStorkSearch: ' + str);
  stork_input.value = str;
  stork_input.dispatchEvent(new Event('input', { bubbles: true }));
}

function outFunc() {
  var tooltip = document.getElementById("myTooltip");
  tooltip.innerHTML = "Copy to clipboard";
}

function confirmBib() {
  uploadBib(dt, true);
}

// TODO: when pasting a bib which gives a search hit, it is not possible to import: check what happens
async function processBib(aBibStr, fileName, force = false) {

  var bibStr = aBibStr.trim();
  console.log("processBib: " + bibStr);
  statusAppend("processing bib: " + bibStr);

  try {
    var bibJSONs = bibtexParse.toJSON(bibStr);
    // console.log(bibJSONs);

    for (var bibJSON of bibJSONs) {
      console.log(bibJSON);

      var key = bibJSON.citationKey;
      console.log("key: " + key);

      var sanitisedKey = sanitiseKey(key);
      bibJSON.citationKey = sanitisedKey;

      bibJSON.entryTags = lowerize(bibJSON.entryTags);
      var tags = bibJSON.entryTags;
      // tags = lowerize(bibJSON.entryTags);
      console.log("tags: " + JSON.stringify(tags));

      var title = "";

      if ("title" in tags) {
        title = tags["title"];
      }
      else {
        title = "";
      }

      console.log("title: " + title);

      var searchString = title; //key + " " + title;
      var searchResults = stork.search("sitesearch", searchString);

      if (!force && (searchResults.total_hit_count > 0 && searchResults.results[0].score > 2000)) {
        console.log("bib already exists: " + searchResults.total_hit_count);
        console.log("results: ");
        console.log(searchResults.results)

        stork.search("sitesearch", searchString);
        // triggerStorkSearch(str);
        addButton.style.display = "block";

      }
      else {

        // date-added    = "2018-12-22 10:50:04 +0100",
        var currentdate = new Date(); 
        var datetime =
          currentdate.getFullYear() + "-" +
          (currentdate.getMonth()+1) + "-" +
          currentdate.getDate() + " " +
          currentdate.getHours() + ":" +
          currentdate.getMinutes() + ":" +
          currentdate.getSeconds() +
          " +0100";

        bibJSON.entryTags["date-added"] = datetime;
        console.log(datetime);
        
        var bibStr = bibtexParse.toBibtex([bibJSON], false);
        bibStr = bibStr.trim();
        console.log(bibStr);

        //TODO: at this stage from time to time the key could be garbage
        // and also the filename
        //sanitise it, eg. remove https:// etc              

        openGitHub(key, fileName, bibStr);
      }
    }
  } catch (err) {
    console.error('Failed to parse bib: ', err);
  }
}

async function uploadBib(inp, force = false) {
  console.log("uploadBib: " + inp + ", force: " + force);

  if (force) {
    processBib(bibStr, "", force);
  }
  else {
    var bibFile = inp.files[0];

    let fileName = "";
    
    var reader = new FileReader();
    reader.readAsText(bibFile, "UTF-8");
    reader.onload = function (evt) {
      var bibStr = evt.target.result;

      if (bibFile.name !== null) {
        fileName = bibFile.name;
      }
      
      console.log("File name: " + fileName);
      processBib(bibStr, fileName, force);

    }
    reader.onerror = function (evt) {
      console.log("error reading file");
    }
  }
}

// can get the PDF with https://sci-hub.se/
// look for a url of the form https://moscow.sci-hub.se/864/d09cfcb7e8c9636cb503218595308a11/lasota2006.pdf#navpanes=0&view=FitH

async function getBib(articleUrl) {

    articleUrl = articleUrl.trim();

    // detect arxiv link
    // TODO: handle also https://arxiv.org/abs/math/0703211
    // TODO: handle also https://arxiv.org/pdf/2310.02393.pdf
    // TODO: handle also https://aps.arxiv.org/abs/2307.07460
    if (articleUrl.startsWith("https://arxiv.org/abs/")) {

      var split = articleUrl.split("/");
      var id = split.slice(-1)[0];

      console.log("arxiv id: " + id);

      // https://arxiv.org/abs/2104.14624
      // https://arxiv.org/pdf/2104.14624.pdf
      // https://ui.adsabs.harvard.edu/abs/2021arXiv210414624G/exportcitation

      var year = "20" + id.substring(0, 2);
      // theUrl = "https://ui.adsabs.harvard.edu/abs/" + year + "arXiv" + id.replace(".", "") + "G" + "/exportcitation"
      var theUrl = "https://ui.adsabs.harvard.edu/abs/arXiv:" + id + "/exportcitation";
      getWebPage(theUrl, res => {
        var el = document.createElement('html');
        el.innerHTML = res;

        var els = el.getElementsByClassName('export-textarea');
        var bibStr = els[0].innerText;

        const fileName = id + ".bib";
        processBib(bibStr, fileName);

      });

    }
    // https://www.sciencedirect.com/science/article/pii/S0304397506001964
    // https://www.sciencedirect.com/science/article/abs/pii/S0021869322001302
    else if (articleUrl.startsWith("https://www.sciencedirect.com/science/article/pii/") || 
            articleUrl.startsWith("https://www.sciencedirect.com/science/article/abs/pii/")) {

      statusAppend("detected sciencedirect article");

      getWebPage(articleUrl, res => {
        var el = document.createElement('html');
        el.innerHTML = res;

        var els = el.getElementsByClassName('doi');
        var doi = els[0].innerText;

        doi2bib(doi, bibStr => { processBib(bibStr, ""); });

      });

    }
    // https://dl.acm.org/doi/10.1145/3087604.3087623
    // https://dl.acm.org/doi/abs/10.1145/1113439.1113446
    else if (articleUrl.startsWith("https://dl.acm.org/doi/")) {

      // get last two blocks when splitting by "/"
      var split = articleUrl.split("/");
      var slice = split.slice(-2);
      var doi = slice[0] + "/" + slice[1];
      var doiUrl = "https://doi.org/" + doi;

      doi2bib(doiUrl, bibStr => { processBib(bibStr, ""); });

    }
    // https://epubs.siam.org/doi/abs/10.1137/S0097539793251219
    // https://epubs.siam.org/action/downloadCitation?format=bibtex&include=abs&direct=true&doi=10.1137/S0097539793251219&downloadFileName=siam_S0097539793251219
    else if (articleUrl.startsWith("https://epubs.siam.org/doi/abs/")) {

    }
    // https://inria.hal.science/hal-02885579
    // https://inria.hal.science/hal-02885579/bibtex
    // https://pastel.hal.science/tel-01223284v2
    // https://hal.archives-ouvertes.fr/hal-03466451
    // https://hal.science/tel-04310389
    
    else if (articleUrl.startsWith("https://inria.hal.science/") ||
      articleUrl.startsWith("https://pastel.hal.science/") ||
      articleUrl.startsWith("https://hal.science/") ||
      articleUrl.startsWith("https://hal.archives-ouvertes.fr/")) {

      var halId = "";

      if (articleUrl.includes("hal-")) {
        halId = "hal-" + articleUrl.split("hal-")[1];
      }
      else if (articleUrl.includes("tel-")) {
        halId = "tel-" + articleUrl.split("tel-")[1];
      }

      halId = halId.replace("/", "");
      statusAppend("hal id: " + halId);

      var bibUrl = "https://inria.hal.science/" + halId + "/bibtex";
      getWebPage(bibUrl, bibStr => {
        
        var fileName = halId + ".bib";
        processBib(bibStr, fileName);

      });
      
    }
    // https://link.springer.com/chapter/10.1007/3-540-60915-6_4
    // https://link.springer.com/article/10.1007/s10883-019-09441-w
    // https://link.springer.com/chapter/10.1007/978-3-030-72016-2_16
    else if (articleUrl.startsWith("https://link.springer.com/article/") ||
            articleUrl.startsWith("https://link.springer.com/chapter/")) {

      var doi = articleUrl.split("/").slice(-2).join("/");
      statusAppend("detected springer article, doi: " + doi);

      var articleUrl = "https://doi.org/" + doi;
      doi2bib(articleUrl, bibStr => { processBib(bibStr, ""); });

      // does not always return a doi
      // var sciHubUrl = "https://sci-hub.se/";
      // articleUrl = sciHubUrl + articleUrl;

      // getWebPage(articleUrl, res => {
      //   var el = new DOMParser().parseFromString(res, "text/html");
        
      //   // var els = el.getElementsByClassName('c-bibliographic-information__value');
      //   var div = el.getElementById("doi");
      //   var doi = div.innerText.trim();
      //   var doiUrl = "https://doi.org/" + doi;

      //   doi2bib(doiUrl, bibStr => { processBib(bibStr, ""); });

      // });
      
    }
    // https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CSL.2023.31
    else if (articleUrl.startsWith("https://drops.dagstuhl.de/entities/document/")) {

      // get the doi
      var doi = articleUrl.split("/").slice(-2).join("/");
      statusAppend("detected LIPIcs dagstuhl drops article, doi: " + doi);

      articleUrl = "https://doi.org/" + doi;
      doi2bib(articleUrl, bibStr => { processBib(bibStr, ""); });

    }
    // https://doi.org/10.1007/s10883-019-09441-w
    // dx.doi.org/10.2140/obs.2019.2.119
    // TODO: recognise a doi also without the URL prefix, i.e., just "10.1007/s10883-019-09441-w"
    else if (articleUrl.includes("doi.org")) {

      if (!articleUrl.startsWith("https://")) {
        articleUrl = "https://" + articleUrl;
      }

      // var strippedUrl = articleUrl.substring(8, articleUrl.length);
      doi2bib(articleUrl, bibStr => { processBib(bibStr, ""); });
    }
    else if (isDoi(articleUrl)) {
      console.log("naked doi detected: " + articleUrl);
      articleUrl = "https://doi.org/" + articleUrl;
      doi2bib(articleUrl, bibStr => { processBib(bibStr, ""); });
    }
    else {
      statusAppend("URL not recognised: " + articleUrl);
    }
}

async function updateSearch() {
  console.log("stork update search: " + stork_input.value);
  getBib(stork_input.value);
}

// TODO: if we are creating a new bib entry,
// then also automatically add the dropped pdf to the corresponding git folder

async function uploadPdf(thePdf) {

  console.log(thePdf);
  var fileName = thePdf.name;

  // if we are on an article page,
  // dropping a PDF means "add this PDF to this entry"
  if(document.getElementById('title_label') != null){ // && document.getElementById('PDF_label') == null) {

    uploadFile("bibliographer", thePdf);

  }
  else {
    // match 2304.14575 inside the filename
    var rx = /[0-9][0-9][0-9][0-9]\.[0-9][0-9][0-9][0-9][0-9]/g;
    var matches = rx.exec(fileName);
    var arxivId = "";

    if (matches !== null && matches.length > 0) {
      arxivId = matches[0];
      console.log("arxiv id: " + arxivId);
    }
    else {
      console.log("cannot extract arxiv id");
    }

    var data = await thePdf.arrayBuffer();
    // console.log(data.byteLength);
    // console.log(data);

    var title = "";
    var author = "";

    await pdfjsLib.getDocument(data).promise.then(async doc => {
      // console.log(doc);

      doc.getMarkInfo().then(info => console.log("mark info: " + info));
      doc.getDownloadInfo().then(info => console.log("download info: " + info));
      doc.getFieldObjects().then(info => console.log("field objs: " + info));
      doc.getAttachments().then(info => console.log("attachments: " + info));
      doc.getOutline().then(info => console.log("outline: " + info));
      doc.getPage(1).then(firstPage => {
        console.log("first page: " + firstPage);
        firstPage.getTextContent({ normalizeWhitespace: true }).then(content => {
          console.log("content: " + content);
        });
      });

      var meta = doc.getMetadata();
      meta.then(metadata => {
        
        console.log(metadata);

        var info = metadata.info;
        console.log(info);

        var meta = metadata.metadata;
        console.log(meta);

        var author = info.Author;
        var title = info.Title;
        var creator = info.Creator;
        var subject = info.Subject;

        console.log("author: " + author);
        console.log("title: " + title);
        console.log("creator: " + creator);
        console.log("subject: " + subject);

        // sometimes the title contains an arxiv id
        // arXiv:2210.16580v1  [cs.DB]  29 Oct 2022
        if (title.startsWith("arXiv:")) {
          arxivId = title.split(":")[1].split(" ")[0].split("v")[0];
          console.log("extracted arxiv id from title: " + arxivId);
        }
        else if (title != "") {
          triggerStorkSearch(title);
        }

        var doi = subject.split('doi:').slice(-1) + "";

        // we have an arxiv PDF
        if (arxivId != "") {
          getBib("https://arxiv.org/abs/" + arxivId);
        }
        // we have an HAL PDF
        else if (creator == "HAL") {

        }
        else if (doi !== null && isDoi(doi)) {

          console.log("We scraped a doi from the PDF: " + doi);
          getBib(doi);

        }
      });
    });
  }
}

function detectPaste(event) {
  // event.preventDefault();
  let paste = (event.clipboardData || window.clipboardData).getData("text");
  processBib(paste, "");
};
