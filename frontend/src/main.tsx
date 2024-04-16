import {render} from 'preact'
import {App} from './app.tsx'
import './index.css'
import {QueryClient, QueryClientProvider} from "@tanstack/react-query";
import {ToastContainer} from "react-toastify";
import 'react-toastify/dist/ReactToastify.css';

const queryClient = new QueryClient()

render((
    <QueryClientProvider client={queryClient}>
        <ToastContainer position="top-center" />
        <App/>
    </QueryClientProvider>
), document.getElementById('app')!)
