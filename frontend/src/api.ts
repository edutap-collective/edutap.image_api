import axios from 'axios';
import {CropData} from "./types.ts";
import _ from 'lodash';

const client = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,

})

export async function healthCheck() {
    return await client.get('/')
}

export async function cropImage({file, crop}: { file: File, crop: CropData }) {
    // TODO: send multipart form data, each entry in crop should be a separate field plus the file
    const formData = new FormData()
    formData.append('file', file)

    for (const [key, value] of Object.entries(crop)) {
        formData.append(_.snakeCase(key), String(value))
    }

    console.log("formData", Object.fromEntries(formData.entries()))
    return await client.post('/crop', formData, {headers: {'Content-Type': 'multipart/form-data'}, responseType: 'blob'})
}
