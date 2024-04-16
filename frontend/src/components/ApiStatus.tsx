import {useQuery} from "@tanstack/react-query";
import {FiCheck, FiXCircle} from "react-icons/fi";
import {healthCheck} from "../api.ts";
import clsx from "clsx";
import {useEffect} from "preact/hooks";

interface ApiStatusProps {
    onUpdate: (status: boolean) => void
}

const ApiStatus = ({onUpdate}: ApiStatusProps) => {
    const isApiHealthy = useQuery({queryKey: ['healthCheck'], queryFn: healthCheck})

    useEffect(() => {
        onUpdate(isApiHealthy.isSuccess)
    }, [isApiHealthy.isSuccess])

    return (
        <div role="alert"
             className={clsx("alert", isApiHealthy.isSuccess && "alert-success", isApiHealthy.isError && "alert-error")}>
            {isApiHealthy.isLoading && <span className="loading loading-sm"></span>}
            {isApiHealthy.isError && <FiXCircle/>}
            {isApiHealthy.isSuccess && <FiCheck/>}
            <span>
                {isApiHealthy.isError &&
                    <span>
                        Health check failed. Tried to reach{' '}
                        <a href={import.meta.env.VITE_API_BASE_URL} target="_blank" rel="noreferrer" className="link">
                            {import.meta.env.VITE_API_BASE_URL}
                        </a>. {' '}
                        Check the console for more information.
                    </span>
                }
                {isApiHealthy.isLoading && 'Checking API health...'}
                {isApiHealthy.isSuccess &&
                    <span>
                        API is healthy. {' '}
                        <a href={import.meta.env.VITE_API_BASE_URL + "/docs"} target="_blank" rel="noreferrer"
                           className="link">
                            Docs
                        </a>
                    </span>
                }
                </span>
        </div>
    )
}

export default ApiStatus