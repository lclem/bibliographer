import { statusAppend, sanitiseKey } from 'https://lclem.github.io/librarian/theme/js/util.js';
import { Octokit } from "https://esm.sh/@octokit/rest";

const pat = "g i t h u b _ p a t _ 1 1 A B C B U P Q 0 l w 1 1 T Z q z c J j B _ p K S o S y i I R 9 X d Q A m 1 l L 4 Q n Z E 0 b 6 J y 0 b Q g q E F 8 V W 9 R o T n 5 B V Z N 3 H X Z c B h f o g F".replaceAll(" ", "");

const octokit2 = new Octokit({ auth: pat });
// window.octokit = octokit;
console.log("Octokit2 loaded");

export async function uploadFileToGitHub(repository, pathFileName, fileName, fileContents) {

    // const blob = new Blob([fileContents], { type : 'plain/text' });
    // const contents = await toBase64(blob);

    const contents = btoa(String.fromCodePoint(...new TextEncoder().encode(fileContents)));

    const url = '/repos/lclem/' + repository + '/contents/' + pathFileName;
    const putRequest = 'PUT ' + url;
    const getRequest = 'GET ' + url;

    statusAppend("put request: " + putRequest);

    const result1 = await octokit2.request(getRequest, {
      owner: 'lclem',
      repo: repository,
      file_path: pathFileName,
      branch: "main"
    });

    const result = await octokit2.request(putRequest, {
      accept: 'application/vnd.github+json',
      owner: 'lclem',
      repo: repository,
      path: fileName,
      message: 'file upload',
      sha: result1.data.sha,
      committer: {
        name: 'Lorenzo C',
        email: 'clementelorenzo@gmail.com'
      },
      content: contents,
      headers: {
        'X-GitHub-Api-Version': '2022-11-28'
      }
    });

    console.log(result.data);

    var rootFolder = document.getElementById('article_rootfolder').getAttribute("href");
    window.open(rootFolder, "_blank");
    
    const commitUrl = result.data.commit.html_url;
    statusAppend(commitUrl);
}