import {FiImage} from "react-icons/fi";
import {useMutation} from "@tanstack/react-query";
import {useEffect, useState} from "preact/hooks";
import {toast} from "react-toastify";
import Toast from "./Toast.tsx";
import {cropImage} from "../api.ts";
import {CropData} from "../types.ts";

interface ImageCropProps {
    file: File | null
    crop: CropData | null
}

// TODO: make container to contain image with max width and fixed padding
// TODO: better error handling, there are some errors whith error messages from the server which should be displayed
// TODO: show loading spinner for at least 2 seconds

const ImageCrop = ({file, crop}: ImageCropProps) => {
    const [imageUrl, setImageUrl] = useState<string | undefined>(undefined)
    const {isSuccess, isPending, mutate} = useMutation({
        mutationFn: cropImage,
        onSuccess: (data) => {
            const url = URL.createObjectURL(data.data)
            setImageUrl(url)
        },
        onError: (error) => {
            console.log("error", error)
            toast(<Toast title="Crop Failed" message="An error occurred while cropping the image"/>, {type: "error"})
        },
    })

    useEffect(() => {
        // Reset the crop data if either file or crop is null
        if (!crop && !file) {
            setImageUrl(undefined)
        } else if (crop && file) {
            mutate({file, crop})
        }
    }, [crop, file]);

    if (!file || !crop || isPending) return (
        <div className="grow flex justify-center items-center bg-base-200 rounded border-2 ">
            {isPending ? <span className="loading loading-lg"></span> : <FiImage size={20}/>}
        </div>
    )

    if (!isSuccess) return null

    return (
        <div className="grow flex justify-center items-center bg-base-200 rounded border-2">
            <img src={imageUrl} alt="" width={500}/>
        </div>
    )
}

export default ImageCrop